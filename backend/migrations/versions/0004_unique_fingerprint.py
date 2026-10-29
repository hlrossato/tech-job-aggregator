"""Keep one row per company, title, and location.

Revision ID: 0004
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        DELETE FROM jobs
        WHERE id IN (
            SELECT id FROM (
                SELECT id, row_number() OVER (
                    PARTITION BY fingerprint
                    ORDER BY published_at DESC NULLS LAST, last_seen_at DESC, id DESC
                ) AS rn
                FROM jobs
            ) ranked
            WHERE rn > 1
        )
        """
    )
    op.drop_index("ix_jobs_fingerprint", table_name="jobs")
    op.create_unique_constraint("uq_jobs_fingerprint", "jobs", ["fingerprint"])


def downgrade() -> None:
    op.drop_constraint("uq_jobs_fingerprint", "jobs", type_="unique")
    op.create_index("ix_jobs_fingerprint", "jobs", ["fingerprint"])
