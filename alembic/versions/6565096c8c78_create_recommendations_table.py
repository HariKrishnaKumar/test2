"""create recommendations table

Revision ID: 6565096c8c78
Revises: c7c0d9e1fbe8
Create Date: 2025-09-14

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6565096c8c78'
down_revision = 'c7c0d9e1fbe8'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'recommendations',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        # sa.Column('mobile_number', sa.String(length=20), nullable=False),
        sa.Column('item_id', sa.String(length=100), nullable=False),
        # sa.Column('item_name', sa.String(length=255), nullable=True),
    )
    # ✅ Removed the op.drop_index(...) that was causing issues


def downgrade():
    op.drop_table('recommendations')
