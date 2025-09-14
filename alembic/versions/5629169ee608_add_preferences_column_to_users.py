"""add preferences column to users

Revision ID: 5629169ee608
Revises: 81431b1ca867
Create Date: 2025-09-14 08:48:03.485386

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5629169ee608'
down_revision: Union[str, Sequence[str], None] = '81431b1ca867'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column("users", sa.Column("preferences", sa.String(255), nullable=True))

def downgrade():
    op.drop_column("users", "preferences")
