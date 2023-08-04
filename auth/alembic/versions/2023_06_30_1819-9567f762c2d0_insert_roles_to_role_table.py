"""Insert roles to role table.

Revision ID: 9567f762c2d0
Revises: e17d3197b1fe
Create Date: 2023-06-30 18:19:39.333580

"""
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9567f762c2d0'
down_revision = 'e17d3197b1fe'
branch_labels = None
depends_on = None


def upgrade() -> None:
    role_table = sa.Table(
        'role',
        sa.MetaData(),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
        sa.UniqueConstraint('name'),
        schema='auth'
    )
    op.bulk_insert(
        role_table,
        [
            {'id': uuid.uuid4(), 'name': 'guest', 'description': 'Анонимный пользователь.'},
            {'id': uuid.uuid4(), 'name': 'registered user', 'description': 'Зарегистрированный пользователь.'},
            {'id': uuid.uuid4(), 'name': 'editor', 'description': 'Редактор контента.'},
            {'id': uuid.uuid4(), 'name': 'administrator', 'description': 'Администратор контента.'}
        ]
    )


def downgrade() -> None:
    op.execute('TRUNCATE TABLE auth.role;')
