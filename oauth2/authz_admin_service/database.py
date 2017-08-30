from functools import lru_cache

import logging

import aiopg.sa
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlalchemy.sql.functions as sa_functions
from aiohttp import web

from . import handlers


_logger = logging.getLogger(__name__)


@lru_cache()
def metadata() -> sa.MetaData:
    result = sa.MetaData()

    sa.Table(
        'AccountRolesLog', result,
        sa.Column('id', sa.Integer, index=True, nullable=False, primary_key=True),
        sa.Column('created_at', sa.DateTime, server_default=sa_functions.now(), index=True, nullable=False),
        sa.Column('created_by', sa.Unicode, index=True, nullable=False),
        sa.Column('request_info', sa.UnicodeText, nullable=None),
        sa.Column('account_id', sa.String, index=True, nullable=False),
        sa.Column('action', sa.String(1), index=True, nullable=False),
        sa.Column('role_ids', postgresql.ARRAY(sa.String(32)), nullable=False),
        sa.Index('idx_arl_role_ids', 'role_ids', postgresql_using='gin')
    )

    sa.Table(
        'AccountRoles', result,
        sa.Column('account_id', sa.String, index=True, nullable=False, primary_key=True),
        sa.Column('role_ids', postgresql.ARRAY(sa.String(32)), nullable=False),
        sa.Column('log_id', sa.Integer, sa.ForeignKey('AccountRolesLog.id'),
                  index=True, nullable=False, unique=True),
        sa.Index('idx_ar_role_ids', 'role_ids', postgresql_using='gin')
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
            sa.select([metadata().tables['AccountRoles']])
        ):
            yield row


async def account(request, account_id):
    accountroles_table = metadata().tables['AccountRoles']
    async with request.app['engine'].acquire() as conn:
        result_proxy = await conn.execute(
            sa.select([accountroles_table])
            .where(accountroles_table.c.account_id == account_id)
        )
        return await result_proxy.fetchone()


async def account_names_with_role(request, role_id):
    accountroles_table = metadata().tables['AccountRoles']
    async with request.app['engine'].acquire() as conn:
        async for row in conn.execute(
            sa.select([accountroles_table.c.account_id])
            .where(accountroles_table.c.role_ids.contains(
                sa.cast([role_id], postgresql.ARRAY(sa.String(32))))
            )
        ):
            yield row['account_id']


# async def delete_account(request, id_from_idp):
#     accounts_table = metadata().tables['Accounts']
#     auditlog_table = metadata().tables['AuditLog']
#     accountroles_table = metadata().tables['AccountRoles']
#     async with request.app['engine'].acquire() as conn:
#         async with conn.begin():
#             result_set = await conn.execute(
#                 sa.select([accountroles_table.c.audit_id])
#                 .select_from(
#                     sa.join(accountroles_table, accounts_table)
#                 )
#                 .where(accountroles_table.c.)
#             )
#     async for row in conn.execute(
#         sa.select([accounts_table.c.id_from_idp]).select_from(
#             sa.join(accountroles_table, accounts_table)
#         ).where(accountroles_table.c.role_id == role_id)
#     ):
#         yield row['id_from_idp']
