"""Store sanitized job description HTML.

Revision ID: 0002
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("description_html", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("jobs", "description_html")
