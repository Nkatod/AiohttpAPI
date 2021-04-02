from aiohttp import web
import asyncio
import logging
from app.utils import load_config, DEFAULT_CONFIG_PATH
from app.db import init_db
from app.routes import setup_routes
from aiohttp_swagger import *


async def init_app():
    conf = load_config(DEFAULT_CONFIG_PATH)

    app = web.Application()
    app['config'] = conf
    await init_db(app)
    setup_routes(app)
    setup_swagger(app)
    host, port = conf['host'], conf['port']
    return app, host, port


def main():
    logging.basicConfig(level=logging.WARNING)

    loop = asyncio.get_event_loop()
    app, host, port = loop.run_until_complete(init_app())
    web.run_app(app, host=host, port=port)


if __name__ == '__main__':
    main()
