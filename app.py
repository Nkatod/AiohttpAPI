from aiohttp import web
import asyncio
import logging
import aiohttp_debugtoolbar
from utils import load_config, DEFAULT_CONFIG_PATH
from db import init_db
from routes import setup_routes


async def init():
    conf = load_config(DEFAULT_CONFIG_PATH)

    app = web.Application()
    app['config'] = conf
    aiohttp_debugtoolbar.setup(app)
    db_pool = await init_db(app)
    setup_routes(app)
    host, port = conf['host'], conf['port']
    return app, host, port


def main():
    logging.basicConfig(level=logging.WARNING)

    loop = asyncio.get_event_loop()
    app, host, port = loop.run_until_complete(init())
    web.run_app(app, host=host, port=port)


if __name__ == '__main__':
    main()
