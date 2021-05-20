from sqlalchemy import create_engine, MetaData

from app.db import tables_list
from app.utils import DEFAULT_CONFIG_PATH, load_config

DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"

ADMIN_DB_URL = DSN.format(
    user='postgres', password='1234', database='postgres',
    host='localhost', port=5432
)

admin_engine = create_engine(ADMIN_DB_URL, isolation_level="AUTOCOMMIT")

USER_CONFIG_PATH = DEFAULT_CONFIG_PATH
USER_CONFIG = load_config(USER_CONFIG_PATH)
USER_DB_URL = DSN.format(**USER_CONFIG['postgres'])
user_engine = create_engine(USER_DB_URL)


def setup_db(config):
    db_name = config['database']
    db_user = config['user']
    db_pass = config['password']

    with admin_engine.connect() as conn:
        conn.execute("DROP DATABASE IF EXISTS %s" % db_name)
        conn.execute("DROP ROLE IF EXISTS %s" % db_user)
        conn.execute("CREATE USER %s WITH PASSWORD '%s'" % (db_user, db_pass))
        conn.execute("CREATE DATABASE %s ENCODING 'UTF8'" % db_name)
        conn.execute("GRANT ALL PRIVILEGES ON DATABASE %s TO %s" %
                     (db_name, db_user))


def create_tables(engine=user_engine):
    meta = MetaData()
    meta.create_all(bind=engine, tables=tables_list)


def drop_tables(engine=user_engine):
    meta = MetaData()
    meta.drop_all(bind=engine, tables=tables_list)


def test_connection(engine=user_engine):
    with engine.connect() as con:
        rs = con.execute('select 1')
    try:
        if rs.rowcount == 1:
            return True
        else:
            return False
    except Exception as e:
        return False


if __name__ == '__main__':
    setup_db(USER_CONFIG['mysql'])
    create_tables(engine=user_engine)
    # sample_data(engine=user_engine)
    print(test_connection(user_engine))
    # drop_tables()
