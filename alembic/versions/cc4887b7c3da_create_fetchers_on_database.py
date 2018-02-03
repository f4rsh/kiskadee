"""Create fetchers on database.

Revision ID: cc4887b7c3da
Revises: 9ee67bf38f1f
Create Date: 2018-01-07 17:29:41.020856

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer
import kiskadee


# revision identifiers, used by Alembic.
revision = 'cc4887b7c3da'
down_revision = '9ee67bf38f1f'
branch_labels = None
depends_on = None


def upgrade():
    fetchers_table = table('fetchers',
            column('id', Integer),
            column('name', String),
            column('target', String),
            column('description', String)
            )

    fetchers = kiskadee.load_fetchers()
    db_session = kiskadee.database.Database().session
    for idx, fetcher in enumerate(fetchers):
        _fetcher = fetcher.Fetcher()
        op.bulk_insert(fetchers_table,
                [
                    {
                        'id': idx, 'name': _fetcher.name,
                        'target': _fetcher.config['target'],
                        'description': _fetcher.config['description']
                        }
                    ]
                )

    def downgrade():
        """TODO: Add a downgrade description."""
    pass
