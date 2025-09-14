"""add recommendations table

Revision ID: b9ade4e55d43
Revises: 6565096c8c78
Create Date: 2025-09-14

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b9ade4e55d43'
down_revision = '6565096c8c78'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'recommendations',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('clover_item_id', sa.String(100), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )


def downgrade():
    op.drop_table('recommendations')
