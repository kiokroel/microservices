"""add subscription key and subscribers table

Revision ID: 7f2f3c0b2a1d
Revises: 0cdb7d8913fa
Create Date: 2025-11-18 10:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7f2f3c0b2a1d"
down_revision: Union[str, Sequence[str], None] = "0cdb7d8913fa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users", sa.Column("subscription_key", sa.Text(), nullable=True))

    op.create_table(
        "subscribers",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("subscriber_id", sa.UUID(), nullable=False),
        sa.Column("author_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["subscriber_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["author_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ux_sub", "subscribers", ["subscriber_id", "author_id"], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ux_sub", table_name="subscribers")
    op.drop_table("subscribers")
    op.drop_column("users", "subscription_key")

