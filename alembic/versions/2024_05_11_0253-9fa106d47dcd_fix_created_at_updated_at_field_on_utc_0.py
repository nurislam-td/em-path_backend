"""fix created_at, updated_at field on utc+0

Revision ID: 9fa106d47dcd
Revises: e08b0c83c843
Create Date: 2024-05-11 02:53:12.344801

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9fa106d47dcd"
down_revision: Union[str, None] = "e08b0c83c843"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "refresh_token",
        "created_at",
        server_default=sa.text("(now() at time zone 'utc')"),
    )
    op.alter_column(
        "refresh_token",
        "updated_at",
        server_default=sa.text("(now() at time zone 'utc')"),
    )
    op.alter_column(
        "verify_code",
        "created_at",
        server_default=sa.text("(now() at time zone 'utc')"),
    )

    # ### end Alembic commands ###


def downgrade() -> None:
    op.alter_column(
        "refresh_token",
        "created_at",
        server_default=sa.text("now()"),
    )
    op.alter_column(
        "refresh_token",
        "updated_at",
        server_default=sa.text("now()"),
    )
    op.alter_column(
        "verify_code",
        "created_at",
        server_default=sa.text("now()"),
    )
