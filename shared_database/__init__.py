"""
"""

from sqlalchemy import (create_engine, MetaData, Table, Column, ForeignKey, Index, UniqueConstraint, Integer, String, Unicode, UnicodeText)
from sqlalchemy.engine.url import URL as ENGINE_URL

engine = create_engine(
    ENGINE_URL(
        'postgresql+psycopg2',
        username='authuser',
        password='authpassword',
        host='localhost',
        port=5432,
        database='authz'
    ),
    isolation_level='SERIALIZABLE',
    client_encoding='utf8'
)

metadata = MetaData()

dataset = Table(
    'dataset', metadata,
    Column('dataset_id', Integer, primary_key=True),
    Column('name', Unicode(255), nullable=True),
    Column('description', UnicodeText(), nullable=True)
)

user = Table(
    'user', metadata,
    Column('user_id', Integer, primary_key=True),
    Column('idp_id', Integer, nullable=False),
    Column('idp_user_id', Integer, primary_key=True),
    Column('email', String(255), nullable=True),
    Column('name', Unicode(255), nullable=True),
    UniqueConstraint('idp_id', 'idp_user_id'),
    Index('idx_idp_user_id', 'idp_user_id')
)

permission_group = Table(
    'permission_group', metadata,
    Column('permission_group_id', Integer, primary_key=True),
    Column('name', Unicode(255), nullable=True),
    Column('description', UnicodeText(), nullable=True)
)

permission = Table(
    'permission', metadata,
    Column('permission_id', Integer, primary_key=True),
    Column('name', Unicode(255), nullable=True),
    Column('description', UnicodeText(), nullable=True),
    Column('dataset_id', Integer,
           ForeignKey('dataset.dataset_id',
                      onupdate='CASCADE', ondelete='CASCADE'),
           nullable=False)
)

permission_to_permission_group = Table(
    'p2pg', metadata,
    Column('permission_id', Integer(),
           ForeignKey('permission.permission_id',
                      onupdate='CASCADE', ondelete='CASCADE'),
           nullable=False),
    Column('permission_group_id', Integer(),
           ForeignKey('permission_group.permission_group_id',
                      onupdate='CASCADE', ondelete='CASCADE'),
           nullable=False),
    UniqueConstraint('permission_id', 'permission_group_id'),
    Index('idx_permission_group_id', 'permission_group_id')
)

permission_to_user = Table(
    'p2u', metadata,
    Column('permission_id', Integer(),
           ForeignKey('permission.permission_id',
                      onupdate='CASCADE', ondelete='CASCADE'),
           nullable=False),
    Column('user_id', Integer(),
           ForeignKey('user.user_id',
                      onupdate='CASCADE', ondelete='CASCADE'),
           nullable=False),
    UniqueConstraint('permission_id', 'user_id'),
    Index('idx_user_id', 'user_id')
)
metadata.drop_all(engine, checkfirst=True)
#metadata.create_all(engine)

tables = (dataset, user, permission_group, permission, permission_to_permission_group)
metadata.create_all(engine, tables)
