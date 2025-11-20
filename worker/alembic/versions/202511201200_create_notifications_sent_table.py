"""create notifications_sent table

Revision ID: 202511201200
Revises:
Create Date: 2025-11-20 15:25:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "202511201200"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notifications_sent",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("subscriber_id", sa.UUID(), nullable=False),
        sa.Column("post_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "subscriber_id",
            "post_id",
            name="ux_notifications_sent_subscriber_post",
        ),
    )


def downgrade() -> None:
    op.drop_table("notifications_sent")

