"""update foreign_key

Revision ID: 2e499c8c97f2
Revises: e2b74cc89a85
Create Date: 2024-03-01 22:37:12.231363

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2e499c8c97f2"
down_revision: Union[str, None] = "e2b74cc89a85"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "refresh_token_user_id_fkey", "refresh_token", type_="foreignkey"
    )
    op.create_foreign_key(None, "refresh_token", "user", ["user_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint(
        "refresh_token_user_id_fkey", "refresh_token", type_="foreignkey"
    )
    op.create_foreign_key(
        "refresh_token_user_id_fkey", "refresh_token", "user", ["user_id"], ["user_id"]
    )
