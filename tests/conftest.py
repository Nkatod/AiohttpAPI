# pytest tests/test_integration.py --pdb

import asyncio
import pytest



import sys
from app.main import init_app
from app.utils import DEFAULT_CONFIG_PATH, load_config
from init_db import (
    setup_db,
    create_tables,
    drop_tables,
    user_engine
)

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
loop = asyncio.get_event_loop_policy().new_event_loop()



@pytest.fixture
async def client(loop, aiohttp_client):
    app, host, port = await init_app()
    return await aiohttp_client(app)



def full_database_reset():
    test_config = load_config(DEFAULT_CONFIG_PATH)
    #setup_db(test_config['mysql'])
    drop_tables(user_engine)
    create_tables(user_engine)


full_database_reset()
