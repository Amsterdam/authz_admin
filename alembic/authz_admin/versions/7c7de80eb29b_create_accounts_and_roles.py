"""create_accounts_and_roles

Revision ID: 7c7de80eb29b
Revises:
Create Date: 2017-08-17 18:06:00.870815

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.sql.functions as sa_functions

# revision identifiers, used by Alembic.
revision = '7c7de80eb29b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    def audit_id():
        return sa.Column('audit_id', sa.Integer, sa.ForeignKey('AuditLog.id'),
                         index=True, nullable=False, unique=True)

    op.create_table(
        'AuditLog',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('created_at', sa.DateTime, server_default=sa_functions.now(), index=True, nullable=False),
        sa.Column('created_by', sa.Integer, index=True, nullable=False),
        sa.Column('table_name', sa.String, index=True, nullable=False),
        sa.Column('foreign_key', sa.Integer, index=True, nullable=False),
        sa.Column('action', sa.String(1), index=True, nullable=False),
        sa.Column('values', sa.UnicodeText, nullable=True),
        sa.Column('context', sa.UnicodeText, nullable=None)
    )

    op.create_table(
        'Accounts',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('id_from_idp', sa.String, index=True, nullable=False, unique=True),
        audit_id()
    )

    op.create_table(
        'AccountRoles',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('account_id', sa.Integer,
                  sa.ForeignKey('Accounts.id', ondelete='CASCADE', onupdate='CASCADE'),
                  index=True, nullable=False),
        sa.Column('role_id', sa.String,
                  index=True, nullable=False),
        sa.Column('grounds', sa.UnicodeText, nullable=False),
        audit_id(),
        sa.UniqueConstraint('user_id', 'role_id')
    )


def downgrade():
    op.drop_table('AccountRoles')
    op.drop_table('Accounts')
    op.drop_table('AuditLog')
