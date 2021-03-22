from aiohttp import web
import asyncio
import logging
import json
import pathlib
import aiohttp_debugtoolbar
from utils import load_config

PROJ_ROOT = pathlib.Path(__file__).parent


async def handle(request):
    test_status = {'status': 'OK'}
    return web.Response(text=json.dumps(test_status), status=200)


async def exception_handler(request):
    raise NotImplementedError


async def init(loop):
    conf = load_config(PROJ_ROOT / 'config' / 'config.yml')

    app = web.Application(loop=loop)
    aiohttp_debugtoolbar.setup(app)
    app.router.add_get('/', handle)
    app.router.add_route('GET', '/exc', exception_handler,
                         name='exc_example')

    host, port = conf['host'], conf['port']
    return app, host, port


def main():
    logging.basicConfig(level=logging.WARNING)

    loop = asyncio.get_event_loop()
    app, host, port = loop.run_until_complete(init(loop))
    web.run_app(app, host=host, port=port)


if __name__ == '__main__':
    main()
