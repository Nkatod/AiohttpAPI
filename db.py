<<<<<<< HEAD
from aiomysql.sa import create_engine
from sqlalchemy.sql.expression import text
from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, String, Date, Boolean
)

DSN = "mysql+mysqldb://{user}:{password}@{host}:{port}/{database}"

meta = MetaData()


class DBEngine(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DBEngine, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        pass

    @property
    def db_engine(self):
        return self.__db_engine

    @db_engine.setter
    def db_engine(self, engine):
        self.__db_engine = engine


_users_table = Table(
    'users', meta,

    Column('user_id', Integer, primary_key=True),
    Column('login', String(50), nullable=False),
    Column('password', String(50), nullable=False)
)


class UsersTable:
    @property
    def users_table(self):
        return _users_table

    @staticmethod
    async def check_user_if_exists(user_name) -> bool:
        engine = DBEngine().db_engine
        async with engine.acquire() as conn:
            sql_text = text('select login from users where login=:login;')
            rs = await conn.execute(sql_text, login=user_name)
        return rs.rowcount > 0

    @staticmethod
    async def create_new_user(login: str, password: str) -> bool:
        engine = DBEngine().db_engine
        async with engine.acquire() as conn:
            sql_text = text('INSERT INTO users (login, password) VALUES(:login, :password);')
            result = await conn.execute(sql_text, login=login, password=password)
            await conn.execute('commit')
        return result


items_table = Table(
    'items', meta,

    Column('item_id', Integer, primary_key=True),
    Column('user_id',
           Integer,
           ForeignKey('users.user_id', ondelete='CASCADE'))
)

token_keys = Table(
    'tokens', meta,

    Column('token_id', Integer, primary_key=True),
    Column('token', String(50), nullable=False),
    Column('Expires', Date, nullable=False),
    Column('user_id',
           Integer,
           ForeignKey('users.user_id', ondelete='CASCADE'))
)

items_transport = Table(
    'itemsTransport', meta,

    Column('transport_id', Integer, primary_key=True),
    Column('reference', String(150), nullable=False),
    Column('confirmed', Boolean, nullable=False, default=False),
    Column('user_sender',
           Integer,
           ForeignKey('users.user_id', ondelete='CASCADE')),
    Column('user_receiver',
           Integer,
           ForeignKey('users.user_id', ondelete='CASCADE'))
)

tables_list = [UsersTable.users_table,
               items_table,
               token_keys,
               items_transport]


class RecordNotFound(Exception):
    """Requested record in database was not found"""


async def init_db(app):
    conf = app['config']['mysql']
    engine = await create_engine(user=conf['user'], db=conf['database'],
                                 host=conf['host'], password=conf['password'])
    app['db_engine'] = engine
    db_engine = DBEngine()
    db_engine.db_engine = engine


async def close_db(app):
    app['db'].close()
    await app['db'].wait_closed()
=======
from aiomysql.sa import create_engine
from sqlalchemy.sql.expression import text
from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, String, Date, Boolean
)

DSN = "mysql+mysqldb://{user}:{password}@{host}:{port}/{database}"

meta = MetaData()


class DBEngine(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DBEngine, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        pass

    @property
    def db_engine(self):
        return self.__db_engine

    @db_engine.setter
    def db_engine(self, engine):
        self.__db_engine = engine


_users_table = Table(
    'users', meta,

    Column('user_id', Integer, primary_key=True),
    Column('login', String(50), nullable=False),
    Column('password', String(50), nullable=False)
)


class UsersTable:
    @property
    def users_table(self):
        return _users_table

    @staticmethod
    async def check_user_if_exists(user_name) -> bool:
        engine = DBEngine().db_engine
        async with engine.acquire() as conn:
            sql_text = text('select login from users where login=:login;')
            rs = await conn.execute(sql_text, login=user_name)
        return rs.rowcount > 0

    @staticmethod
    async def create_new_user(login: str, password: str) -> bool:
        engine = DBEngine().db_engine
        async with engine.acquire() as conn:
            sql_text = text('INSERT INTO users (login, password) VALUES(:login, :password);')
            result = await conn.execute(sql_text, login=login, password=password)
            await conn.execute('commit')
        return result


items_table = Table(
    'items', meta,

    Column('item_id', Integer, primary_key=True),
    Column('user_id',
           Integer,
           ForeignKey('users.user_id', ondelete='CASCADE'))
)

token_keys = Table(
    'tokens', meta,

    Column('token_id', Integer, primary_key=True),
    Column('token', String(50), nullable=False),
    Column('Expires', Date, nullable=False),
    Column('user_id',
           Integer,
           ForeignKey('users.user_id', ondelete='CASCADE'))
)

items_transport = Table(
    'itemsTransport', meta,

    Column('transport_id', Integer, primary_key=True),
    Column('reference', String(150), nullable=False),
    Column('confirmed', Boolean, nullable=False, default=False),
    Column('user_sender',
           Integer,
           ForeignKey('users.user_id', ondelete='CASCADE')),
    Column('user_receiver',
           Integer,
           ForeignKey('users.user_id', ondelete='CASCADE'))
)

tables_list = [UsersTable.users_table,
               items_table,
               token_keys,
               items_transport]


class RecordNotFound(Exception):
    """Requested record in database was not found"""


async def init_db(app):
    conf = app['config']['mysql']
    engine = await create_engine(user=conf['user'], db=conf['database'],
                                 host=conf['host'], password=conf['password'])
    app['db_engine'] = engine
    db_engine = DBEngine()
    db_engine.db_engine = engine


async def close_db(app):
    app['db'].close()
    await app['db'].wait_closed()
>>>>>>> 4b0356d9b8929b4372a010fce368bc581a064d8f
