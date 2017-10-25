"""Auto generate a migration to the following tables.

* reports
* analysis
* versions
* analyzers

Revision ID: 48dd292b5a80
Revises: d2989db85795
Create Date: 2017-10-19 10:32:42.008412

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '48dd292b5a80'
down_revision = 'd2989db85795'
branch_labels = None
depends_on = None


def upgrade():
    """Create tables: reports, analysis, versions, analyzers."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'analyzers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Unicode(length=255), nullable=False),
        sa.Column('version', sa.Unicode(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_table(
        'versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('number', sa.Unicode(length=100), nullable=False),
        sa.Column('package_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['package_id'], ['packages.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('number', 'package_id')
    )
    op.create_table(
        'analysis',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('version_id', sa.Integer(), nullable=False),
        sa.Column('analyzer_id', sa.Integer(), nullable=False),
        sa.Column('raw', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['analyzer_id'], ['analyzers.id'], ),
        sa.ForeignKeyConstraint(['version_id'], ['versions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('analysis_id', sa.Integer(), nullable=False),
        sa.Column('results', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['analysis_id'], ['analysis.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    """Drop the tables created at upgrade."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('reports')
    op.drop_table('analysis')
    op.drop_table('versions')
    op.drop_table('analyzers')
    # ### end Alembic commands ###
