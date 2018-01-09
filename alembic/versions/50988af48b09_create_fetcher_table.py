"""create fetcher table.

Revision ID: 50988af48b09
Revises: 6daaf1d5cfee
Create Date: 2017-10-17 16:48:26.940294

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '50988af48b09'
down_revision = '6daaf1d5cfee'
branch_labels = None
depends_on = None


def upgrade():
    """Create table fetchers."""
    op.create_table(
        'fetchers',
        sa.Column(
            'id',
            sa.Integer,
            sa.Sequence(
                'fetchers_id_seq',
                optional=True
            ),
            primary_key=True
        ),
        sa.Column('name', sa.Unicode(255), nullable=False, unique=True),
        sa.Column('source', sa.Unicode(255), nullable=True),
        sa.Column('description', sa.UnicodeText)
    )


def downgrade():
    """Drop table fetchers."""
    op.drop_table('fetchers')
