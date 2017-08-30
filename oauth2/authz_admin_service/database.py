from functools import lru_cache

import logging

import aiopg.sa
import sqlalchemy as sa
import sqlalchemy.engine.url as sa_url
import sqlalchemy.sql.functions as sa_functions
from aiohttp import web

from . import handlers


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
        user=config['user'],
        database=config['dbname'],
        host=config['host'],
        port=config['port'],
        password=config['password'],
        client_encoding='utf8'
    )


async def accounts(request):
    async with request.app['engine'].acquire() as conn:
        async for row in conn.execute(
            sa.select([metadata().tables['Accounts']])
        ):
            yield row


async def account(request, id_from_idp):
    accounts_table = metadata().tables['Accounts']
    async with request.app['engine'].acquire() as conn:
        result_set = await conn.execute(
            sa.select([accounts_table])
            .where(accounts_table.c.id_from_idp == id_from_idp)
        )
        return await result_set.fetchone()


async def accountroles(request, account_id):
    table_accountroles = metadata().tables['AccountRoles']
    async with request.app['engine'].acquire() as conn:
        async for row in conn.execute(
            sa.select([table_accountroles])
            .where(table_accountroles.c.account_id == account_id)
        ):
            yield row


async def accountrole(request, account_id_from_idp, role_id):
    accounts_table = metadata().tables['Accounts']
    accountroles_table = metadata().tables['AccountRoles']
    async with request.app['engine'].acquire() as conn:
        result_set = await conn.execute(
            sa.select([accountroles_table]).select_from(
                sa.join(accountroles_table, accounts_table)
            ).where(
                accounts_table.c.id_from_idp == account_id_from_idp and
                accountroles_table.c.role_id == role_id
            )
        )
        return await result_set.fetchone()


async def account_names_with_role(request, role_id):
    accounts_table = metadata().tables['Accounts']
    accountroles_table = metadata().tables['AccountRoles']
    async with request.app['engine'].acquire() as conn:
        async for row in conn.execute(
            sa.select([accounts_table.c.id_from_idp]).select_from(
                sa.join(accountroles_table, accounts_table)
            ).where(accountroles_table.c.role_id == role_id)
        ):
            yield row['id_from_idp']
