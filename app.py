from aiohttp import web

if __name__ == '__main__':
    my_app = web.Application()
    web.run_app(my_app)