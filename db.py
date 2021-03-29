from aiomysql.sa import create_engine
from sqlalchemy.sql.expression import text
from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, String, Date, Boolean
)
from security import generate_password_hash

DSN = "mysql+mysqldb://{user}:{password}@{host}:{port}/{database}"

meta = MetaData()


class DBEngine(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DBEngine, cls).__new__(cls)
        return cls.instance

    @property
    def db_engine(self):
        return self.__db_engine

    @db_engine.setter
    def db_engine(self, engine):
        if not hasattr(self, '__db_engine'):
            self.__db_engine = engine


_users_table = Table(
    'users', meta,

    Column('user_id', Integer, primary_key=True),
    Column('login', String(50), nullable=False),
    Column('password', String(100), nullable=False)
)


class UsersTable:
    @property
    def users_table(self):
        return _users_table

    @staticmethod
    async def check_user_if_exists(user_name) -> int:
        engine = DBEngine().db_engine
        async with engine.acquire() as conn:
            sql_text = text('select user_id from users where login=:login;')
            q_result = await conn.execute(sql_text, login=user_name)
            if q_result.rowcount > 1:
                raise ValueError('DB Many users found')
            res = await q_result.fetchall()
            result = None
            if q_result.rowcount == 1:
                result = res[0][0]
        return result

    @staticmethod
    async def create_new_user(login: str, password: str) -> bool:
        engine = DBEngine().db_engine
        password_hash = generate_password_hash(password)
        async with engine.acquire() as conn:
            sql_text = text('INSERT INTO users (login, password) VALUES(:login, :password);')
            result = await conn.execute(sql_text, login=login, password=password_hash)
            await conn.execute('commit')
        return result

    @staticmethod
    async def get_password_hash(login: str) -> str:
        engine = DBEngine().db_engine
        async with engine.acquire() as conn:
            sql_text = text('select password from users where login=:login;')
            result = await conn.execute(sql_text, login=login)
            if result.rowcount != 1:
                raise ValueError('DB Many users found')
            res = await result.fetchall()
        return res[0][0]

    def __init__(self):
        self.users_list = []

    async def get_all_users(self):
        engine = DBEngine().db_engine
        async with engine.acquire() as conn:
            sql_text = text('select user_id, login from users')
            result = await conn.execute(sql_text)
            for val in (await result.fetchall()):
                self.users_list.append({'user_id': val[0], 'login': val[1]})


_items_table = Table(
    'items', meta,

    Column('item_id', Integer, primary_key=True),
    Column('attr1', String(50), nullable=False),
    Column('user_id',
           Integer,
           ForeignKey('users.user_id', ondelete='CASCADE'))
)

class ItemsTable:
    @property
    def items_table(self):
        return _items_table

    async def create_new_item(self, user_id, attr1:str):
        engine = DBEngine().db_engine
        async with engine.acquire() as conn:
            sql_text = text('INSERT INTO items (user_id, attr1) VALUES(:user_id, :attr1);')
            result = await conn.execute(sql_text, user_id=user_id, attr1=attr1)
            await conn.execute('commit')
        return result

    async def delete_item(self, user_id:str, item_id:str):
        engine = DBEngine().db_engine
        async with engine.acquire() as conn:
            sql_text = text('DELETE FROM items where item_id = :item_id and user_id = :user_id ;')
            result = await conn.execute(sql_text, user_id=user_id, item_id=item_id)
            await conn.execute('commit')
        return result

    async def get_user_items(self, user_id) -> list:
        engine = DBEngine().db_engine
        item_list = []
        async with engine.acquire() as conn:
            sql_text = text('select item_id, attr1 from items where user_id = :user_id ;')
            result = await conn.execute(sql_text, user_id=user_id)
            for val in (await result.fetchall()):
                item_list.append({'item_id': val[0], 'attr1': val[1]})
        return item_list

token_keys = Table(
    'tokens', meta,

    Column('token_id', Integer, primary_key=True),
    Column('token', String(100), nullable=False),
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

tables_list = [_users_table,
               _items_table,
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
