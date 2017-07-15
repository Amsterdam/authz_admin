import aiopg
import contextlib
import psycopg2
import psycopg2.errorcodes


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
            dsn = 'dbname={} user={} password={} host={} port={}'.format(
                self._config['dbname'],
                self._config['user'],
                self._config['password'],
                self._config['host'],
                self._config['port']
            )
            self._pool = await aiopg.create_pool(dsn)

    async def __aenter__(self):
        await self._connect()
        return self._pool

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if isinstance(exc_type, psycopg2.Error):
            if not await self._is_usable():
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
            with await self._pool as conn:
                await conn.execute("SELECT 1")
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
        await cursor.execute("""
            CREATE TABLE "KeyValuePairs"
            (
                key character varying COLLATE pg_catalog."en_US.utf8" NOT NULL,
                value text COLLATE pg_catalog."en_US.utf8",
                CONSTRAINT "KeyValuePairs_pkey" PRIMARY KEY (key)
            )
            WITH (
                OIDS=FALSE
            );
            ALTER TABLE public."KeyValuePairs"
                OWNER TO oauth2;
            INSERT INTO "KeyValuePairs"
                ("key", "value")
            VALUES ('schema_version', '1');
        """)
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
