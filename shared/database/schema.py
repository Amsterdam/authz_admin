"""

This module can either be imported or run as a standalone script.

Example 1: Run from within python::

    from shared.database.schema import create
    create()

Example 2: Run from the command line::

    python -m shared.schema

"""

from sqlalchemy import (create_engine, MetaData, Table, Column, ForeignKey, Index, UniqueConstraint, Integer, String, Unicode, UnicodeText)
from sqlalchemy.engine.url import URL as ENGINE_URL


def create():
    """ Creates the database schema.

    .. todo:: Accept an open psycopg2 connection as a parameter?

    :raise: All kind of SQLAlchemy exceptions if schema creation fails.

    """
    engine = create_engine(
        ENGINE_URL(
            'postgresql+psycopg2',
            username='authuser',
            password='authpassword',
            host='localhost',
            port=5432,
            database='authz'
        ),
        # isolation_level='SERIALIZABLE',
        client_encoding='utf8'
    )

    metadata = MetaData(engine)

    # dataset = \
    Table(
        'dataset', metadata,
        Column('dataset_id', Integer, primary_key=True),
        Column('name', Unicode(255), nullable=True),
        Column('description', UnicodeText(), nullable=True)
    )

    # user = \
    Table(
        'user', metadata,
        Column('user_id', Integer, primary_key=True),
        Column('idp_id', Integer, nullable=False),
        Column('idp_user_id', Integer, nullable=False),
        Column('email', String(255), nullable=True),
        Column('name', Unicode(255), nullable=True),
        UniqueConstraint('idp_id', 'idp_user_id'),
        Index('idx_user_idp_user_id', 'idp_user_id')
    )

    # permission_group = \
    Table(
        'permission_group', metadata,
        Column('permission_group_id', Integer, primary_key=True),
        Column('name', Unicode(255), nullable=True),
        Column('description', UnicodeText(), nullable=True)
    )

    # permission = \
    Table(
        'permission', metadata,
        Column('permission_id', Integer, primary_key=True),
        Column('name', Unicode(255), nullable=True),
        Column('description', UnicodeText(), nullable=True),
        Column('dataset_id', Integer,
               ForeignKey('dataset.dataset_id',
                          onupdate='CASCADE', ondelete='CASCADE'),
               nullable=False)
    )

    # permission_to_permission_group = \
    Table(
        'p2pg', metadata,
        Column('permission_id', Integer,
               ForeignKey('permission.permission_id',
                          onupdate='CASCADE', ondelete='CASCADE'),
               nullable=False),
        Column('permission_group_id', Integer,
               ForeignKey('permission_group.permission_group_id',
                          onupdate='CASCADE', ondelete='CASCADE'),
               nullable=False),
        UniqueConstraint('permission_id', 'permission_group_id'),
        Index('idx_p2pg_permission_group_id', 'permission_group_id')
    )

    # permission_to_user = \
    Table(
        'p2u', metadata,
        Column('permission_id', Integer,
               ForeignKey('permission.permission_id',
                          onupdate='CASCADE', ondelete='CASCADE'),
               nullable=False),
        Column('user_id', Integer,
               ForeignKey('user.user_id',
                          onupdate='CASCADE', ondelete='CASCADE'),
               nullable=False),
        UniqueConstraint('permission_id', 'user_id'),
        Index('idx_p2u_user_id', 'user_id')
    )

    metadata.drop_all(checkfirst=True)
    metadata.create_all(checkfirst=True)


if __name__ == '__main__':
    create()
