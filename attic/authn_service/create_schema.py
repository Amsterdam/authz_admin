"""

This module can either be imported or run as a standalone script.

Example 1: Run from within python::

    from shared.database.schema import create
    create()

Example 2: Run from the command line::

    python -m shared.schema

"""

import sqlalchemy as sa
import sqlalchemy.engine.url as sa_url
import sqlalchemy.sql.functions as sa_functions
from functools import lru_cache

from oauth2.config import load as load_config


@lru_cache()
def metadata() -> sa.MetaData:
    result = sa.MetaData()


    def audit_id():
        return sa.Column('audit_id', sa.Integer, sa.ForeignKey('AuditLog.id'), index=True, nullable=False, unique=True)

    sa.Table(
        'KeyValuePairs', result,
        sa.Column('key', sa.Unicode(255), nullable=False, primary_key=True),
        sa.Column('value', sa.UnicodeText)
    )

    sa.Table(
        'AuditLog', result,
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('created_at', sa.DateTime, index=True, nullable=False,
                  server_default=sa_functions.now()),
        sa.Column('created_by', sa.Integer, index=True, nullable=False),
        sa.Column('table_name', sa.String, index=True, nullable=False),
        sa.Column('foreign_key', sa.Integer, index=True, nullable=False),
        sa.Column('action', sa.String(1), index=True, nullable=False),
        sa.Column('values', sa.UnicodeText, nullable=True),
        sa.Column('context', sa.UnicodeText, nullable=None)
    )

    sa.Table(
        'Users', result,
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('idp_id', sa.Integer, index=True, nullable=False),
        sa.Column('idp_user_id', sa.Integer, nullable=False),
        audit_id(),
        sa.UniqueConstraint('idp_id', 'idp_user_id')
    )

    sa.Table(
        'UserRoles', result,
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer,
                  sa.ForeignKey('Users.id', ondelete='CASCADE'),
                  index=True, nullable=False),
        sa.Column('role_id', sa.String,
                  index=True, nullable=False),
        sa.Column('grounds', sa.UnicodeText, nullable=False),
        audit_id(),
        sa.UniqueConstraint('user_id', 'role_id'),
    )

    return result


def _create_schema_with_engine(engine):
    # language=rst
    """Creates the database schema.

    .. todo:: Accept an open psycopg2 connection as a parameter?

    :raises: All kinds of SQLAlchemy exceptions if schema creation fails.

    """

    md = metadata()

    md.drop_all(bind=engine, checkfirst=True)
    md.create_all(bind=engine, checkfirst=True)
    engine.connect().execute(
        md.tables['KeyValuePairs'].insert().values(key='schema_version', value='1')
    )


def create_schema(config):
    engine = sa.create_engine(
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
    _create_schema_with_engine(engine)
    engine.dispose()


def main():
    config = load_config()['postgres']
    create_schema(config)


if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    main()
