from functools import lru_cache

import logging

import aiopg.sa
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlalchemy.sql.functions as sa_functions
import sqlalchemy.exc as sa_exceptions
from aiohttp import web


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


async def accounts(request, role_ids=None):
    accountroles = metadata().tables['AccountRoles']
    statement = sa.select([accountroles])
    if role_ids is not None:
        statement = statement.where(accountroles.c.role_ids.contains(
            sa.cast(role_ids, postgresql.ARRAY(sa.String(32)))
        ))
    async with request.app['engine'].acquire() as conn:
        async for row in conn.execute(
            statement
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


async def delete_account(request, account):
    account_data = await account.data()
    accountroleslog = metadata().tables['AccountRolesLog']
    accountroles = metadata().tables['AccountRoles']
    async with request.app['engine'].acquire() as conn:
        async with conn.begin():
            result_set = await conn.execute(
                accountroleslog.insert().values(
                    created_by='p.van.beek@amsterdam.nl',
                    request_info=str(request.headers),
                    account_id=account['account'],
                    action='D',
                    role_ids=account_data['role_ids']
                ).returning(
                    accountroleslog.c.id
                )
            )
            row = await result_set.fetchone()
            log_id = row[0]
            result_set = await conn.execute(
                accountroles.delete().where(sa.and_(
                    accountroles.c.account_id == account['account'],
                    accountroles.c.log_id == account_data['log_id']
                ))
            )
            if result_set.rowcount != 1:
                raise web.HTTPPreconditionFailed()
    return log_id


async def update_account(request, account, role_ids):
    account_data = await account.data()
    accountroleslog = metadata().tables['AccountRolesLog']
    accountroles = metadata().tables['AccountRoles']
    async with request.app['engine'].acquire() as conn:
        async with conn.begin():
            result_set = await conn.execute(
                accountroleslog.insert().values(
                    created_by='p.van.beek@amsterdam.nl',
                    request_info=str(request.headers),
                    account_id=account['account'],
                    action='U',
                    role_ids=role_ids
                ).returning(
                    accountroleslog.c.id
                )
            )
            row = await result_set.fetchone()
            log_id = row[0]
            result_set = await conn.execute(
                accountroles.update().where(sa.and_(
                    accountroles.c.account_id == account['account'],
                    accountroles.c.log_id == account_data['log_id']
                )).values(
                    role_ids=role_ids,
                    log_id=log_id
                )
            )
            if result_set.rowcount != 1:
                raise web.HTTPPreconditionFailed()
    return log_id


async def create_account(request, account_id, role_ids):
    accountroleslog = metadata().tables['AccountRolesLog']
    accountroles = metadata().tables['AccountRoles']
    async with request.app['engine'].acquire() as conn:
        async with conn.begin():
            result_set = await conn.execute(
                accountroleslog.insert().values(
                    created_by='p.van.beek@amsterdam.nl',
                    request_info=str(request.headers),
                    account_id=account_id,
                    action='C',
                    role_ids=role_ids
                ).returning(accountroleslog.c.id)
            )
            row = await result_set.fetchone()
            log_id = row[0]
            try:
                await conn.execute(
                    accountroles.insert().values(
                        account_id=account_id,
                        role_ids=role_ids,
                        log_id=log_id
                    )
                )
            except sa_exceptions.IntegrityError:
                raise web.HTTPPreconditionFailed()

    return log_id

