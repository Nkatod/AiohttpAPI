from aiomysql.sa import create_engine
from sqlalchemy.sql.expression import text
from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, String, Boolean
)
from security import generate_password_hash
from pandas import DataFrame

DSN = "mysql+mysqldb://{user}:{password}@{host}:{port}/{database}"

meta = MetaData()


class DBEngine(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DBEngine, cls).__new__(cls)
            cls.__db_engine = None
        return cls.instance

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

    async def get_login_by_id(self, user_id: int) -> DataFrame:
        engine = DBEngine().db_engine
        async with engine.acquire() as conn:
            sql_text = text('SELECT login from users where user_id = :user_id;')
            result_query = await conn.execute(sql_text, user_id=user_id)
            item_list = []
            for val in (await result_query.fetchall()):
                item_list.append({'login': val[0], })
            result = DataFrame(item_list)
        return result

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
           ForeignKey('users.user_id', ondelete='CASCADE'),
           nullable=False)
)


class ItemsTable:
    @property
    def items_table(self):
        return _items_table

    async def create_new_item(self, user_id, attr1: str):
        engine = DBEngine().db_engine
        async with engine.acquire() as conn:
            sql_text = text('INSERT INTO items (user_id, attr1) VALUES(:user_id, :attr1);')
            result = await conn.execute(sql_text, user_id=user_id, attr1=attr1)
            await conn.execute('COMMIT')
        return result

    async def delete_item(self, user_id: int, item_id: int):
        engine = DBEngine().db_engine
        async with engine.acquire() as conn:
            sql_text = text('DELETE FROM items where item_id = :item_id and user_id = :user_id ;')
            result = await conn.execute(sql_text, user_id=user_id, item_id=item_id)
            await conn.execute('COMMIT')
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


items_transport = Table(
    'itemsTransport', meta,

    Column('transport_id', Integer, primary_key=True),
    Column('item_id',
           Integer,
           ForeignKey('items.item_id', ondelete='CASCADE'),
           nullable=False),
    Column('reference', String(150), nullable=False),
    Column('confirmed', Boolean, nullable=False, default=False),
    Column('user_sender',
           Integer,
           ForeignKey('users.user_id', ondelete='CASCADE'),
           nullable=False),
    Column('user_receiver',
           Integer,
           ForeignKey('users.user_id', ondelete='CASCADE'),
           nullable=False)
)


class ItemsTransportTable:
    async def create_send_to(self, reference: str, user_receiver_id: int, user_sender_id: int,
                             item_id: int) -> DataFrame:
        engine = DBEngine().db_engine
        result = DataFrame()
        async with engine.acquire() as conn:
            sql_text = text('INSERT INTO itemsTransport (item_id, reference, user_sender, user_receiver, confirmed) '
                            'VALUES(:item_id, :reference, :user_sender, :user_receiver, :confirmed) ;')
            result_query = await conn.execute(sql_text,
                                              item_id=item_id,
                                              reference=reference,
                                              user_sender=user_sender_id,
                                              user_receiver=user_receiver_id,
                                              confirmed=False)
            await conn.execute('COMMIT')
            if result_query.rowcount == 1:
                result = DataFrame([{'reference': reference,
                                     'item_id': item_id,
                                     'user_sender': user_sender_id,
                                     'user_receiver': user_receiver_id,
                                     'confirmed': False}])
        return result

    async def get_transfer(self, reference: str, user_receiver_id: int) -> DataFrame:
        engine = DBEngine().db_engine
        result = DataFrame()
        async with engine.acquire() as conn:
            sql_text = text('SELECT reference, item_id, user_sender, user_receiver, confirmed '
                            'FROM itemsTransport where user_receiver = :user_receiver and reference = :reference ;')
            result_query = await conn.execute(sql_text,
                                              reference=reference,
                                              user_receiver=user_receiver_id)
            item_list = []
            for val in (await result_query.fetchall()):
                item_list.append({'reference': val[0],
                                  'item_id': val[1],
                                  'user_sender': val[2],
                                  'user_receiver': val[3],
                                  'confirmed': val[4]})
            result = DataFrame(item_list)
        return result

    async def move_to(self, reference: str, user_receiver_id: int, user_sender_id: int,
                      item_id: int) -> DataFrame:
        engine = DBEngine().db_engine
        result = DataFrame()
        try:
            async with engine.acquire() as conn:
                sql_text = text('UPDATE itemsTransport '
                                'SET confirmed = 1 '
                                'WHERE reference = :reference ;')
                result_query_update = await conn.execute(sql_text, reference=reference)
                if result_query_update.rowcount != 1:
                    # Error of changing owner
                    return result
                # change owner of item
                sql_text = text('UPDATE items '
                                'SET user_id = :user_id '
                                'WHERE item_id = :item_id ;')
                result_change_owner = await conn.execute(sql_text, user_id=user_receiver_id, item_id=item_id)
                if result_change_owner.rowcount != 1:
                    # Error of changing owner
                    return result

                sql_text = text('DELETE FROM itemsTransport '
                                'WHERE confirmed = 0 '
                                'and item_id = :item_id '
                                'and user_sender = :user_sender '
                                'and user_receiver = :user_receiver ;')
                result_query_delete = await conn.execute(sql_text,
                                                         item_id=item_id,
                                                         user_sender=user_sender_id,
                                                         user_receiver=user_receiver_id)
                await conn.execute('COMMIT')

                result = DataFrame([{'reference': reference,
                                     'item_id': item_id,
                                     'user_sender': user_sender_id,
                                     'user_receiver': user_receiver_id,
                                     'confirmed': True}])
        except Exception as e:
            pass
        return result


tables_list = [_users_table,
               _items_table,
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
