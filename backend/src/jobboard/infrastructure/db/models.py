from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from jobboard.infrastructure.db.base import Base


class CompanyModel(Base):
    __tablename__ = "companies"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    website_url: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    jobs: Mapped[list["JobModel"]] = relationship(back_populates="company")


class SourceModel(Base):
    __tablename__ = "sources"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    key: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    base_url: Mapped[str] = mapped_column(Text)
    adapter: Mapped[str] = mapped_column(String(80))
    locale: Mapped[str | None] = mapped_column(String(20))
    crawl_frequency_minutes: Mapped[int] = mapped_column(default=1440)
    rate_limit_per_second: Mapped[float] = mapped_column(Float, default=1.0)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    compliance_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    jobs: Mapped[list["JobModel"]] = relationship(back_populates="source")
    crawl_runs: Mapped[list["CrawlRunModel"]] = relationship(back_populates="source")


class JobTechnologyModel(Base):
    __tablename__ = "job_technologies"

    job_id: Mapped[UUID] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True
    )
    technology_id: Mapped[UUID] = mapped_column(
        ForeignKey("technologies.id", ondelete="CASCADE"), primary_key=True
    )


class TechnologyModel(Base):
    __tablename__ = "technologies"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)


class JobModel(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        UniqueConstraint("source_id", "external_id", name="uq_jobs_source_external"),
        Index("ix_jobs_status_published", "status", "published_at"),
        Index("ix_jobs_country_status", "country_code", "status"),
        Index("ix_jobs_fingerprint", "fingerprint"),
        Index("ix_jobs_search_vector", "search_vector", postgresql_using="gin"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    source_id: Mapped[UUID] = mapped_column(ForeignKey("sources.id", ondelete="RESTRICT"))
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id", ondelete="RESTRICT"))
    external_id: Mapped[str | None] = mapped_column(String(255))
    fingerprint: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text)
    canonical_url: Mapped[str] = mapped_column(Text)
    apply_url: Mapped[str] = mapped_column(Text)
    location_text: Mapped[str | None] = mapped_column(String(500))
    country_code: Mapped[str | None] = mapped_column(String(2), index=True)
    remote_scope: Mapped[str | None] = mapped_column(String(120))
    workplace_type: Mapped[str] = mapped_column(String(20), default="unspecified", index=True)
    employment_type: Mapped[str | None] = mapped_column(String(80), index=True)
    seniority: Mapped[str | None] = mapped_column(String(80), index=True)
    salary_min: Mapped[int | None] = mapped_column(Integer)
    salary_max: Mapped[int | None] = mapped_column(Integer)
    salary_currency: Mapped[str | None] = mapped_column(String(3))
    language: Mapped[str | None] = mapped_column(String(10))
    role_category: Mapped[str | None] = mapped_column(String(80), index=True)
    classification_confidence: Mapped[float | None] = mapped_column(Float)
    classification_reason: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    search_vector: Mapped[str | None] = mapped_column(TSVECTOR)

    source: Mapped[SourceModel] = relationship(back_populates="jobs")
    company: Mapped[CompanyModel] = relationship(back_populates="jobs")
    technologies: Mapped[list[TechnologyModel]] = relationship(
        secondary="job_technologies", lazy="selectin"
    )


class CrawlRunModel(Base):
    __tablename__ = "crawl_runs"
    __table_args__ = (Index("ix_crawl_runs_source_started", "source_id", "started_at"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    source_id: Mapped[UUID] = mapped_column(ForeignKey("sources.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(30), default="running")
    item_count: Mapped[int] = mapped_column(default=0)
    error_count: Mapped[int] = mapped_column(default=0)
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    source: Mapped[SourceModel] = relationship(back_populates="crawl_runs")
