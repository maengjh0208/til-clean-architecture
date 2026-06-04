"""empty message

Revision ID: caa7442efc12
Revises: f68ea4b1d8d0
Create Date: 2026-06-04 05:22:30.705270

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "caa7442efc12"
down_revision: Union[str, None] = "f68ea4b1d8d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "user",
        "created_at",
        existing_type=sa.DateTime(),
        nullable=False,
        server_default=sa.text("CURRENT_TIMESTAMP"),
    )
    op.alter_column(
        "user",
        "updated_at",
        existing_type=sa.DateTime(),
        nullable=False,
        server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "user",
        "created_at",
        existing_type=sa.DateTime(),
        nullable=False,
        server_default=None,
    )
    op.alter_column(
        "user",
        "updated_at",
        existing_type=sa.DateTime(),
        nullable=False,
        server_default=None,
    )
