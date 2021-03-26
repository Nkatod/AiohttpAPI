import models
from aiohttp import web
import json

async def handle(request):
    test_status = {'status': 'OK'}
    return web.Response(text=json.dumps(test_status), status=200)


async def register_new_user(request):
    try:
        login = request.query['user']
        password = request.query['password']
        user = await models.UserCreator.create_new_user(login, password)
        print("New user created: ", user.login, user.password)
        response_obj = {'status': 'success', 'user_id': user.user_id, 'user': login, 'password': password}
        return web.Response(text=json.dumps(response_obj), status=200)
    except Exception as e:
        response_obj = {'status': 'failed', 'reason': str(e)}
        return web.Response(text=json.dumps(response_obj), status=500)


async def exception_handler(request):
    raise NotImplementedError
