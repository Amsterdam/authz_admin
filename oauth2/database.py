import contextlib
import logging

import aiopg
import psycopg2
import psycopg2.errorcodes

_logger = logging.getLogger(__name__)


SQL_CREATE_TABLE_KEYVALUEPAIRS = """
SET client_encoding = 'UTF8';
SET default_with_oids = false;
CREATE SEQUENCE "role_role_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
CREATE SEQUENCE "user_user_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
CREATE TABLE "KeyValuePairs" (
    "key" character varying COLLATE "pg_catalog"."en_US.utf8" NOT NULL,
    "value" "text" COLLATE "pg_catalog"."en_US.utf8",
    CONSTRAINT "KeyValuePairs_pkey" PRIMARY KEY ("key")
);
CREATE TABLE "Role" (
    "role_id" integer DEFAULT "nextval"('"role_role_id_seq"'::"regclass") NOT NULL,
    "idp_id" character varying,
    "idp_role_id" character varying,
    CONSTRAINT "role_primary_key" PRIMARY KEY ("role_id"),
    CONSTRAINT "unique_idp_role" UNIQUE ("idp_id", "idp_role_id")
);
CREATE TABLE "Role_Profile" (
    "role_id" integer NOT NULL,
    "profile_id" integer NOT NULL,
    CONSTRAINT "role_profile_primary_key" PRIMARY KEY ("role_id", "profile_id")
);
CREATE TABLE "User" (
    "user_id" integer DEFAULT "nextval"('"user_user_id_seq"'::"regclass") NOT NULL,
    "idp_id" character varying,
    "idp_user_id" character varying,
    CONSTRAINT "unique_idp_user" UNIQUE ("idp_id", "idp_user_id"),
    CONSTRAINT "user_primary_key" PRIMARY KEY ("user_id")
);
CREATE TABLE "User_Profile" (
    "user_id" integer NOT NULL,
    "profile_id" integer NOT NULL,
    CONSTRAINT "user_profile_primary_key" PRIMARY KEY ("user_id", "profile_id")
);
INSERT INTO "KeyValuePairs" VALUES ('schema_version', '1');
SELECT pg_catalog.setval('"role_role_id_seq"', 1, false);
SELECT pg_catalog.setval('"user_user_id_seq"', 1, false);
CREATE INDEX "index_role_idp_id" ON "Role" USING "btree" ("idp_id");
CREATE INDEX "index_role_idp_role_id" ON "Role" USING "btree" ("idp_role_id");
CREATE INDEX "index_role_profile_profile_id" ON "Role_Profile" USING "btree" ("profile_id");
CREATE INDEX "index_role_profile_role_id" ON "Role_Profile" USING "btree" ("role_id");
CREATE INDEX "index_user_idp_id" ON "User" USING "btree" ("idp_id");
CREATE INDEX "index_user_idp_user_id" ON "User" USING "btree" ("idp_user_id");
CREATE INDEX "index_user_profile_profile_id" ON "User_Profile" USING "btree" ("profile_id");
CREATE INDEX "index_user_profile_user_id" ON "User_Profile" USING "btree" ("user_id");
ALTER TABLE ONLY "Role_Profile"
    ADD CONSTRAINT "role_profile_2_role" FOREIGN KEY ("role_id") REFERENCES "Role"("role_id") ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY "User_Profile"
    ADD CONSTRAINT "user_profile_2_user" FOREIGN KEY ("user_id") REFERENCES "User"("user_id") ON UPDATE CASCADE ON DELETE CASCADE;
"""


class ConnectionPool:
    # language=rst
    """Postgres connection pool. Attempts recovery on errors.

    Usage::

        from database import ConnectionPool
        connection_pool = ConnectionPool(config)
        async with connection_pool as pool:
            with await pool.cursor() as cur:
                await cur.execute('DROP TABLE IF EXISTS tbl')

    """

    def __init__(self, config):
        # language=rst
        """

        :param dict config: Postgres configuration info.

        """
        self._config = config
        self._pool = None

    async def _connect(self):
        if self._pool is None:
            dsn = 'dbname={dbname} user={user} password={password} host={host} ' \
                  'port={port}'.format_map(self._config)
            _logger.info(
                'Connecting to database psql://{user}@{host}:{port}/{dbname}'.
                    format_map(self._config)
            )
            self._pool = await aiopg.create_pool(dsn)

    async def __aenter__(self):
        await self._connect()
        # if not await self._is_usable():
        #     await self._unset_pool()
        #     await self._set_pool()
        return self._pool

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if isinstance(exc_type, psycopg2.Error):
            if not await self._is_usable():
                await self._disconnect()

    async def _disconnect(self):
        with contextlib.suppress(psycopg2.Error):
            self._pool.terminate()
            await self._pool.wait_closed()
        self._pool = None

    async def _is_usable(self):
        # language=rst
        """Checks whether the connectionpool is usable.

        :returns boolean: True if we can query the database, False otherwise

        """
        try:
            with await self._pool.cursor() as cursor:
                _logger.debug("""await cursor.execute("SELECT 1")""")
                await cursor.execute("SELECT 1")
        except psycopg2.Error:
            return False
        else:
            return True


async def _put_schema(cursor):
    try:
        await cursor.execute("""
            SELECT "value" FROM "KeyValuePairs"
            WHERE "key" = 'schema_version';
        """)
    except psycopg2.Error as e:
        if e.pgcode != psycopg2.errorcodes.UNDEFINED_TABLE:
            raise
        await cursor.execute(SQL_CREATE_TABLE_KEYVALUEPAIRS)
        schema_version = 1
    else:
        if cursor.rowcount == 0:
            raise Exception("No entry 'schema_version' in table 'KeyValuePairs'.")
        row = await cursor.fetchone()
        schema_version = int(row[0])
    if schema_version != 1:
        raise Exception("Strange schema version: {}".format(schema_version))


async def put_schema(app):
    # language=rst
    """Creates or updates the database schema.

    :param aiohttp.web.Application app: Unused, but this procedure is called with
        this parameter by aiohttp during application startup, so we must accept
        it to prevent errors.

    """
    async with app['connection_pool'] as pool:
        with await pool.cursor() as cursor:
            await _put_schema(cursor)
