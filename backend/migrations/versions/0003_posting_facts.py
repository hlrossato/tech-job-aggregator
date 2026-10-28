"""Store team, offices, and remote location from the public posting.

Revision ID: 0003
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("team", sa.String(length=255), nullable=True))
    op.add_column("jobs", sa.Column("office_locations", sa.Text(), nullable=True))
    op.add_column("jobs", sa.Column("remote_location", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("jobs", "remote_location")
    op.drop_column("jobs", "office_locations")
    op.drop_column("jobs", "team")
