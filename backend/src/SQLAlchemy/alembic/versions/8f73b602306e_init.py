"""init

Revision ID: 8f73b602306e
Revises:
Create Date: 2023-11-29 16:55:01.839452

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "8f73b602306e"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "deutsche_Staedte",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("plz", sa.Integer, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("deutsche_Staedte")
