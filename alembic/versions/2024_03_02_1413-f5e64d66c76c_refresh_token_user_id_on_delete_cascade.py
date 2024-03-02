"""refresh_token.user_id on delete -> cascade

Revision ID: f5e64d66c76c
Revises: 2e499c8c97f2
Create Date: 2024-03-02 14:13:38.579483

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f5e64d66c76c"
down_revision: Union[str, None] = "2e499c8c97f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "refresh_token_user_id_fkey", "refresh_token", type_="foreignkey"
    )
    op.create_foreign_key(
        "refresh_token_user_id_fkey",
        "refresh_token",
        "user",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "refresh_token_user_id_fkey", "refresh_token", type_="foreignkey"
    )
    op.create_foreign_key(
        "refresh_token_user_id_fkey",
        "refresh_token",
        "user",
        ["user_id"],
        ["id"],
    )
