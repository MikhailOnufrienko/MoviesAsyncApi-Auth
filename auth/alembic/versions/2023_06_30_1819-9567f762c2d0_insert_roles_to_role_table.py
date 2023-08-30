"""Insert roles to role table.

Revision ID: 9567f762c2d0
Revises: e17d3197b1fe
Create Date: 2023-06-30 18:19:39.333580

"""
import uuid

from alembic import op
from sqlalchemy import Table

from auth.src.models.entity import metadata_obj


# revision identifiers, used by Alembic.
revision = '9567f762c2d0'
down_revision = 'e17d3197b1fe'
branch_labels = None
depends_on = None


def upgrade() -> None:
    role_table = Table('role', metadata_obj)

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
