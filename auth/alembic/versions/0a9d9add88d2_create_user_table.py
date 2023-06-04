"""Create user table.

Revision ID: 0a9d9add88d2
Revises: d609f7a5bc1b
Create Date: 2023-06-04 14:46:41.891600

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0a9d9add88d2'
down_revision = 'd609f7a5bc1b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False, primary_key=True),
        sa.Column('login', sa.String(), nullable=False, unique=True),
        sa.Column('password', sa.String(), nullable=False)
    )


def downgrade() -> None:
    op.drop_table('users')
