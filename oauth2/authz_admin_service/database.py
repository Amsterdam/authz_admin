from functools import lru_cache

import logging

import aiopg.sa
import sqlalchemy as sa
import sqlalchemy.engine.url as sa_url
import sqlalchemy.sql.functions as sa_functions
from aiohttp import web

from oauth2.config import load as load_config


_logger = logging.getLogger(__name__)


@lru_cache()
def metadata() -> sa.MetaData:
    result = sa.MetaData()

    def audit_id():
        return sa.Column('audit_id', sa.Integer, sa.ForeignKey('AuditLog.id'),
                         index=True, nullable=False, unique=True)

    sa.Table(
        'AuditLog', result,
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('created_at', sa.DateTime, server_default=sa_functions.now(), index=True, nullable=False),
        sa.Column('created_by', sa.Integer, index=True, nullable=False),
        sa.Column('table_name', sa.String, index=True, nullable=False),
        sa.Column('foreign_key', sa.Integer, index=True, nullable=False),
        sa.Column('action', sa.String(1), index=True, nullable=False),
        sa.Column('values', sa.UnicodeText, nullable=True),
        sa.Column('context', sa.UnicodeText, nullable=None)
    )

    sa.Table(
        'Accounts', result,
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('id_from_idp', sa.String, index=True, nullable=False, unique=True),
        audit_id()
    )

    sa.Table(
        'AccountRoles', result,
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('account_id', sa.Integer,
                  sa.ForeignKey('Accounts.id', ondelete='CASCADE', onupdate='CASCADE'),
                  index=True, nullable=False),
        sa.Column('role_id', sa.String,
                  index=True, nullable=False),
        sa.Column('grounds', sa.UnicodeText, nullable=False),
        audit_id(),
        sa.UniqueConstraint('account_id', 'role_id')
    )

    return result


def create_engine(config):
    return aiopg.sa.create_engine(
        sa_url.URL(
            'postgresql+psycopg2',
            username=config['user'],
            password=config['password'],
            host=config['host'],
            port=config['port'],
            database=config['dbname']
        ),
        # isolation_level='SERIALIZABLE',
        client_encoding='utf8'
    )


async def all_account_ids(request: web.Request):
    pass
