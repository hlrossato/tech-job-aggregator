"""Initial job aggregation schema.

Revision ID: 0001
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.create_table(
        "companies",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("website_url", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_companies_name", "companies", ["name"])
    op.create_table(
        "sources",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("key", sa.String(120), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("base_url", sa.Text(), nullable=False),
        sa.Column("adapter", sa.String(80), nullable=False),
        sa.Column("locale", sa.String(20)),
        sa.Column("crawl_frequency_minutes", sa.Integer(), nullable=False, server_default="1440"),
        sa.Column("rate_limit_per_second", sa.Float(), nullable=False, server_default="1"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("compliance_notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_sources_key", "sources", ["key"])
    op.create_table(
        "technologies",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
    )
    op.create_index("ix_technologies_name", "technologies", ["name"])
    op.create_index("ix_technologies_slug", "technologies", ["slug"])
    op.create_table(
        "jobs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("sources.id", ondelete="RESTRICT")),
        sa.Column("company_id", sa.Uuid(), sa.ForeignKey("companies.id", ondelete="RESTRICT")),
        sa.Column("external_id", sa.String(255)),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("canonical_url", sa.Text(), nullable=False),
        sa.Column("apply_url", sa.Text(), nullable=False),
        sa.Column("location_text", sa.String(500)),
        sa.Column("country_code", sa.String(2)),
        sa.Column("remote_scope", sa.String(120)),
        sa.Column("workplace_type", sa.String(20), nullable=False, server_default="unspecified"),
        sa.Column("employment_type", sa.String(80)),
        sa.Column("seniority", sa.String(80)),
        sa.Column("salary_min", sa.Integer()),
        sa.Column("salary_max", sa.Integer()),
        sa.Column("salary_currency", sa.String(3)),
        sa.Column("language", sa.String(10)),
        sa.Column("role_category", sa.String(80)),
        sa.Column("classification_confidence", sa.Float()),
        sa.Column("classification_reason", sa.Text()),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column(
            "search_vector",
            postgresql.TSVECTOR(),
            sa.Computed(
                "setweight(to_tsvector('simple', coalesce(title, '')), 'A') || "
                "setweight(to_tsvector('simple', coalesce(description, '')), 'B')",
                persisted=True,
            ),
        ),
        sa.UniqueConstraint("source_id", "external_id", name="uq_jobs_source_external"),
    )
    op.create_index("ix_jobs_search_vector", "jobs", ["search_vector"], postgresql_using="gin")
    op.create_index("ix_jobs_title_trgm", "jobs", ["title"], postgresql_using="gin", postgresql_ops={"title": "gin_trgm_ops"})
    op.create_index("ix_jobs_status_published", "jobs", ["status", "published_at"])
    op.create_index("ix_jobs_country_status", "jobs", ["country_code", "status"])
    op.create_index("ix_jobs_fingerprint", "jobs", ["fingerprint"])
    for column in ("country_code", "workplace_type", "employment_type", "seniority", "role_category", "status"):
        op.create_index(f"ix_jobs_{column}", "jobs", [column])
    op.create_table(
        "job_technologies",
        sa.Column("job_id", sa.Uuid(), sa.ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("technology_id", sa.Uuid(), sa.ForeignKey("technologies.id", ondelete="CASCADE"), primary_key=True),
    )
    op.create_table(
        "crawl_runs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("sources.id", ondelete="CASCADE")),
        sa.Column("status", sa.String(30), nullable=False, server_default="running"),
        sa.Column("item_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text()),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_crawl_runs_source_started", "crawl_runs", ["source_id", "started_at"])


def downgrade() -> None:
    op.drop_table("crawl_runs")
    op.drop_table("job_technologies")
    op.drop_table("jobs")
    op.drop_table("technologies")
    op.drop_table("sources")
    op.drop_table("companies")
