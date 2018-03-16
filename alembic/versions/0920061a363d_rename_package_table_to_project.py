"""rename package table to project.

Revision ID: 0920061a363d
Revises: cc4887b7c3da
Create Date: 2018-03-13 17:48:05.506903

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0920061a363d'
down_revision = 'cc4887b7c3da'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('packages', 'projects')
    op.alter_column('versions', 'package_id', new_column_name='project_id')


def downgrade():
    op.rename_table('projects', 'packages')
