import re
from datetime import UTC, datetime
from typing import Any, Self
from uuid import UUID

from sqlalchemy import Select, func, or_, select, update
from sqlalchemy.orm import Session, selectinload

from jobboard.domain.models import (
    Facets,
    JobDraft,
    JobSearchCriteria,
    JobStatus,
    JobView,
    SearchResult,
    WorkplaceType,
)
from jobboard.domain.repositories import CrawlRunRepository, JobRepository
from jobboard.infrastructure.db.models import (
    CompanyModel,
    CrawlRunModel,
    JobModel,
    SourceModel,
    TechnologyModel,
)
from jobboard.infrastructure.db.session import SessionFactory


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def _to_view(model: JobModel) -> JobView:
    return JobView(
        id=model.id,
        title=model.title,
        company_name=model.company.name,
        description=model.description,
        canonical_url=model.canonical_url,
        apply_url=model.apply_url,
        location_text=model.location_text,
        country_code=model.country_code,
        workplace_type=WorkplaceType(model.workplace_type),
        employment_type=model.employment_type,
        seniority=model.seniority,
        salary_min=model.salary_min,
        salary_max=model.salary_max,
        salary_currency=model.salary_currency,
        technologies=tuple(technology.name for technology in model.technologies),
        role_category=model.role_category,
        published_at=model.published_at,
        first_seen_at=model.first_seen_at,
    )


class SQLAlchemyJobRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, job_id: UUID) -> JobView | None:
        statement = (
            select(JobModel)
            .options(selectinload(JobModel.company), selectinload(JobModel.technologies))
            .where(JobModel.id == job_id, JobModel.status == JobStatus.ACTIVE.value)
        )
        model = self.session.scalar(statement)
        return _to_view(model) if model else None

    def _filtered(self, criteria: JobSearchCriteria) -> Select[Any]:
        statement = select(JobModel).where(JobModel.status == JobStatus.ACTIVE.value)
        if criteria.query:
            query = func.websearch_to_tsquery("simple", criteria.query)
            statement = statement.where(
                or_(
                    JobModel.search_vector.op("@@")(query),
                    JobModel.title.op("%")(criteria.query),
                )
            )
            if criteria.sort == "relevance":
                statement = statement.order_by(
                    func.ts_rank_cd(JobModel.search_vector, query).desc(),
                    JobModel.published_at.desc().nullslast(),
                )
        if criteria.technologies:
            statement = statement.where(
                JobModel.technologies.any(TechnologyModel.name.in_(criteria.technologies))
            )
        if criteria.role_category:
            statement = statement.where(JobModel.role_category == criteria.role_category)
        if criteria.country_code:
            statement = statement.where(JobModel.country_code == criteria.country_code.upper())
        if criteria.workplace_type:
            statement = statement.where(JobModel.workplace_type == criteria.workplace_type.value)
        if criteria.seniority:
            statement = statement.where(JobModel.seniority == criteria.seniority)
        if criteria.employment_type:
            statement = statement.where(JobModel.employment_type == criteria.employment_type)
        if criteria.posted_after:
            statement = statement.where(JobModel.published_at >= criteria.posted_after)
        if criteria.salary_min is not None:
            statement = statement.where(JobModel.salary_max >= criteria.salary_min)
        if not criteria.query or criteria.sort == "newest":
            statement = statement.order_by(
                JobModel.published_at.desc().nullslast(), JobModel.first_seen_at.desc()
            )
        return statement

    def search(self, criteria: JobSearchCriteria) -> SearchResult:
        filtered = self._filtered(criteria)
        count_statement = select(func.count()).select_from(filtered.order_by(None).subquery())
        total = self.session.scalar(count_statement) or 0
        statement = (
            filtered.options(selectinload(JobModel.company), selectinload(JobModel.technologies))
            .offset((criteria.page - 1) * criteria.page_size)
            .limit(criteria.page_size)
        )
        models = self.session.scalars(statement).all()
        return SearchResult(
            items=tuple(_to_view(model) for model in models),
            total=total,
            page=criteria.page,
            page_size=criteria.page_size,
        )

    def facets(self) -> Facets:
        active = JobStatus.ACTIVE.value
        technologies = dict(
            self.session.execute(
                select(TechnologyModel.name, func.count(JobModel.id))
                .join(JobModel.technologies)
                .where(JobModel.status == active)
                .group_by(TechnologyModel.name)
                .order_by(func.count(JobModel.id).desc())
            ).all()
        )

        def grouped(column: Any) -> dict[str, int]:
            return dict(
                self.session.execute(
                    select(column, func.count(JobModel.id))
                    .where(JobModel.status == active, column.is_not(None))
                    .group_by(column)
                ).all()
            )

        return Facets(
            technologies=technologies,
            countries=grouped(JobModel.country_code),
            role_categories=grouped(JobModel.role_category),
            workplace_types=grouped(JobModel.workplace_type),
        )

    def ensure_source(self, key: str, name: str, base_url: str, adapter: str) -> None:
        source = self.session.scalar(select(SourceModel).where(SourceModel.key == key))
        if source is None:
            self.session.add(SourceModel(key=key, name=name, base_url=base_url, adapter=adapter))
            self.session.flush()
            return
        source.name = name
        source.base_url = base_url
        source.adapter = adapter

    def upsert(self, draft: JobDraft, fingerprint: str) -> UUID:
        source = self.session.scalar(select(SourceModel).where(SourceModel.key == draft.source_key))
        if source is None:
            source = SourceModel(
                key=draft.source_key,
                name=draft.source_name,
                base_url=draft.source_base_url,
                adapter=draft.source_adapter,
            )
            self.session.add(source)
            self.session.flush()

        company = self.session.scalar(
            select(CompanyModel).where(func.lower(CompanyModel.name) == draft.company_name.lower())
        )
        if company is None:
            company = CompanyModel(name=draft.company_name)
            self.session.add(company)
            self.session.flush()

        job = None
        if draft.external_id:
            job = self.session.scalar(
                select(JobModel).where(
                    JobModel.source_id == source.id,
                    JobModel.external_id == draft.external_id,
                )
            )
        if job is None:
            job = self.session.scalar(
                select(JobModel).where(
                    JobModel.source_id == source.id,
                    JobModel.canonical_url == draft.canonical_url,
                )
            )
        values = {
            "company_id": company.id,
            "external_id": draft.external_id,
            "fingerprint": fingerprint,
            "title": draft.title,
            "description": draft.description,
            "canonical_url": draft.canonical_url,
            "apply_url": draft.apply_url,
            "location_text": draft.location_text,
            "country_code": draft.country_code,
            "remote_scope": draft.remote_scope,
            "workplace_type": draft.workplace_type.value,
            "employment_type": draft.employment_type,
            "seniority": draft.seniority,
            "salary_min": draft.salary_min,
            "salary_max": draft.salary_max,
            "salary_currency": draft.salary_currency,
            "language": draft.language,
            "role_category": draft.role_category,
            "classification_confidence": draft.classification_confidence,
            "classification_reason": draft.classification_reason,
            "status": JobStatus.ACTIVE.value,
            "published_at": draft.published_at,
            "expires_at": draft.expires_at,
            "last_seen_at": datetime.now(UTC),
        }
        if job is None:
            job = JobModel(source_id=source.id, **values)
            self.session.add(job)
        else:
            for key, value in values.items():
                setattr(job, key, value)

        technologies: list[TechnologyModel] = []
        for name in sorted(set(draft.technologies)):
            technology = self.session.scalar(
                select(TechnologyModel).where(TechnologyModel.name == name)
            )
            if technology is None:
                technology = TechnologyModel(name=name, slug=_slug(name))
                self.session.add(technology)
            technologies.append(technology)
        job.technologies = technologies
        self.session.flush()
        return job.id

    def expire_unseen(self, source_key: str, seen_before: datetime) -> int:
        source_id = self.session.scalar(select(SourceModel.id).where(SourceModel.key == source_key))
        if source_id is None:
            return 0
        result = self.session.execute(
            update(JobModel)
            .where(
                JobModel.source_id == source_id,
                JobModel.last_seen_at < seen_before,
                JobModel.status == JobStatus.ACTIVE.value,
            )
            .values(status=JobStatus.EXPIRED.value)
        )
        return int(getattr(result, "rowcount", 0) or 0)


class SQLAlchemyCrawlRunRepository:
    def __init__(self, session: Session):
        self.session = session

    def start(self, source_key: str) -> UUID:
        source_id = self.session.scalar(select(SourceModel.id).where(SourceModel.key == source_key))
        if source_id is None:
            raise ValueError(f"Unknown source: {source_key}")
        run = CrawlRunModel(source_id=source_id)
        self.session.add(run)
        self.session.flush()
        return run.id

    def finish(
        self,
        run_id: UUID,
        *,
        status: str,
        item_count: int,
        error_count: int,
        error_message: str | None = None,
    ) -> None:
        run = self.session.get(CrawlRunModel, run_id)
        if run is None:
            raise ValueError(f"Unknown crawl run: {run_id}")
        run.status = status
        run.item_count = item_count
        run.error_count = error_count
        run.error_message = error_message
        run.finished_at = datetime.now(UTC)


class SQLAlchemyUnitOfWork:
    def __init__(self, session_factory: object = SessionFactory):
        self.session_factory = session_factory

    def __enter__(self) -> Self:
        self.session = self.session_factory()  # type: ignore[operator]
        self.jobs: JobRepository = SQLAlchemyJobRepository(self.session)
        self.crawl_runs: CrawlRunRepository = SQLAlchemyCrawlRunRepository(self.session)
        return self

    def __exit__(self, *args: object) -> None:
        if args[0] is not None:
            self.rollback()
        self.session.close()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
