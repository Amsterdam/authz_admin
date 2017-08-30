"""create_accounts_and_roles

Revision ID: 7c7de80eb29b
Revises:
Create Date: 2017-08-17 18:06:00.870815

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlalchemy.sql.functions as sa_functions

# revision identifiers, used by Alembic.
revision = '7c7de80eb29b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():

    op.create_table(
        'AccountRolesLog',
        sa.Column('id', sa.Integer, index=True, nullable=False, primary_key=True),
        sa.Column('created_at', sa.DateTime, server_default=sa_functions.now(), index=True, nullable=False),
        sa.Column('created_by', sa.Unicode, index=True, nullable=False),
        sa.Column('request_info', sa.UnicodeText, nullable=None),
        sa.Column('account_id', sa.String, index=True, nullable=False),
        sa.Column('action', sa.String(1), index=True, nullable=False),
        sa.Column('role_ids', postgresql.ARRAY(sa.String(32)), nullable=False),
        sa.Index('idx_arl_role_ids', 'role_ids', postgresql_using='gin')
    )

    op.create_table(
        'AccountRoles',
        sa.Column('account_id', sa.String, index=True, nullable=False, primary_key=True),
        sa.Column('role_ids', postgresql.ARRAY(sa.String(32)), nullable=False),
        sa.Column('log_id', sa.Integer, sa.ForeignKey('AccountRolesLog.id'),
                  index=True, nullable=False, unique=True),
        sa.Index('idx_ar_role_ids', 'role_ids', postgresql_using='gin')
    )



def downgrade():
    op.drop_table('AccountRoles')
    op.drop_table('Accounts')
    op.drop_table('AuditLog')
