<<<<<<< HEAD
import sqlalchemy as sa
from sqlalchemy import create_engine, MetaData

from db import tables_list, UsersTable, items_table, DSN
from utils import DEFAULT_CONFIG_PATH, load_config

ADMIN_DB_URL = DSN.format(
    user='root', password='admin_pass', database='sys',
    host='localhost', port=3306
)

admin_engine = create_engine(ADMIN_DB_URL, isolation_level="READ UNCOMMITTED")

USER_CONFIG_PATH = DEFAULT_CONFIG_PATH
USER_CONFIG = load_config(USER_CONFIG_PATH)
USER_DB_URL = DSN.format(**USER_CONFIG['mysql'])
user_engine = create_engine(USER_DB_URL)

users_table = UsersTable.users_table


def setup_db(config):
    db_name = config['database']
    db_user = config['user']
    db_pass = config['password']

    with admin_engine.connect() as conn:
        conn.execute("DROP DATABASE IF EXISTS %s" % db_name)
        conn.execute("DROP USER IF EXISTS '%s'@'%s'" % (db_user, 'localhost'))
        conn.execute("CREATE USER '%s'@'%s' IDENTIFIED BY '%s'" % (db_user, 'localhost', db_pass))
        conn.execute("CREATE DATABASE %s" % db_name)
        conn.execute("GRANT ALL PRIVILEGES ON %s.* TO '%s'@'%s'" %
                     (db_name, db_user, 'localhost'))


def create_tables(engine=user_engine):
    meta = MetaData()
    meta.create_all(bind=engine, tables=tables_list)


def drop_tables(engine=user_engine):
    meta = MetaData()
    meta.drop_all(bind=engine, tables=tables_list)


def sample_data(engine=user_engine):
    with engine.connect() as conn:
        conn.execute(users_table.insert(), [
            {'login': 'admin',
             'password': 'admin'}
        ])
        conn.execute(items_table.insert(), [
            {'user_id': 1, },
            {'user_id': 1, },
            {'user_id': 1, },
        ])


def test_connection(engine=user_engine):
    with engine.connect() as con:
        rs = con.execute('select 1')
    try:
        if isinstance(rs, sa.engine.result.ResultProxy) and rs.rowcount == 1:
            print('DB RAW query success')
        else:
            print('DB RAW query failure')
    except Exception as e:
        print('DB RAW query failure', e)


if __name__ == '__main__':
    # setup_db(USER_CONFIG['mysql'])
    # create_tables(engine=user_engine)
    # sample_data(engine=user_engine)
    test_connection(user_engine)
    # drop_tables()
=======
import sqlalchemy as sa
from sqlalchemy import create_engine, MetaData

from db import tables_list, UsersTable, items_table, DSN
from utils import DEFAULT_CONFIG_PATH, load_config

ADMIN_DB_URL = DSN.format(
    user='root', password='admin_pass', database='sys',
    host='localhost', port=3306
)

admin_engine = create_engine(ADMIN_DB_URL, isolation_level="READ UNCOMMITTED")

USER_CONFIG_PATH = DEFAULT_CONFIG_PATH
USER_CONFIG = load_config(USER_CONFIG_PATH)
USER_DB_URL = DSN.format(**USER_CONFIG['mysql'])
user_engine = create_engine(USER_DB_URL)

users_table = UsersTable.users_table


def setup_db(config):
    db_name = config['database']
    db_user = config['user']
    db_pass = config['password']

    with admin_engine.connect() as conn:
        conn.execute("DROP DATABASE IF EXISTS %s" % db_name)
        conn.execute("DROP USER IF EXISTS '%s'@'%s'" % (db_user, 'localhost'))
        conn.execute("CREATE USER '%s'@'%s' IDENTIFIED BY '%s'" % (db_user, 'localhost', db_pass))
        conn.execute("CREATE DATABASE %s" % db_name)
        conn.execute("GRANT ALL PRIVILEGES ON %s.* TO '%s'@'%s'" %
                     (db_name, db_user, 'localhost'))


def create_tables(engine=user_engine):
    meta = MetaData()
    meta.create_all(bind=engine, tables=tables_list)


def drop_tables(engine=user_engine):
    meta = MetaData()
    meta.drop_all(bind=engine, tables=tables_list)


def sample_data(engine=user_engine):
    with engine.connect() as conn:
        conn.execute(users_table.insert(), [
            {'login': 'admin',
             'password': 'admin'}
        ])
        conn.execute(items_table.insert(), [
            {'user_id': 1, },
            {'user_id': 1, },
            {'user_id': 1, },
        ])


def test_connection(engine=user_engine):
    with engine.connect() as con:
        rs = con.execute('select 1')
    try:
        if isinstance(rs, sa.engine.result.ResultProxy) and rs.rowcount == 1:
            print('DB RAW query success')
        else:
            print('DB RAW query failure')
    except Exception as e:
        print('DB RAW query failure', e)


if __name__ == '__main__':
    # setup_db(USER_CONFIG['mysql'])
    # create_tables(engine=user_engine)
    # sample_data(engine=user_engine)
    test_connection(user_engine)
    # drop_tables()
>>>>>>> 4b0356d9b8929b4372a010fce368bc581a064d8f
