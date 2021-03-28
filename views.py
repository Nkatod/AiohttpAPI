import models
from aiohttp import web
import json


async def handle(request):
    test_status = {'status': 'OK'}
    return web.Response(text=json.dumps(test_status, indent=4), status=200)


class UsersView:
    @staticmethod
    async def register_new_user(request):
        try:
            login = request.query['login']
            password = request.query['password']
            response_result, user = await models.UserCreator().create_new_user(login, password)
            if response_result.status != 200:
                return web.Response(text=json.dumps(response_result.response_obj, indent=4),
                                    status=response_result.status)
            return web.Response(text=json.dumps(response_result.response_obj, indent=4), status=200)
        except Exception as e:
            response_obj = {'status': 'failed', 'reason': str(e)}
            return web.Response(text=json.dumps(response_obj, indent=4), status=500)

    @staticmethod
    async def get_all_users(request):
        try:
            users_list = await models.UserCreator.get_all_users()
            response_obj = {'status': 'success', 'users_list': users_list}
            return web.Response(text=json.dumps(response_obj, indent=4), status=200)
        except Exception as e:
            response_obj = {'status': 'failed', 'reason': str(e)}
            return web.Response(text=json.dumps(response_obj, indent=4), status=500)

    @staticmethod
    async def authorization(request):
        try:
            login = request.query['login']
            password = request.query['password']

            response_result, curr_user = await models.authenticate_by_login_password(login, password)
            if response_result.status != 200:
                return web.Response(text=json.dumps(response_result.response_obj, indent=4),
                                    status=response_result.status)

            response_obj = {'status': 'success', 'token': curr_user.token.toJson()}
            return web.Response(text=json.dumps(response_obj, indent=4), status=200)
        except Exception as e:
            response_obj = {'status': 'failed', 'reason': str(e)}
            return web.Response(text=json.dumps(response_obj, indent=4), status=500)


class ItemsView:
    @staticmethod
    async def create_new_item(request):
        try:
            response_result, item = await models.ItemCreator().create_new_item(request)
            if response_result.status != 200:
                return web.Response(text=json.dumps(response_result.response_obj, indent=4),
                                    status=response_result.status)
            response_obj = {'status': 'success', 'item': item.toJson()}
            return web.Response(text=json.dumps(response_obj, indent=4), status=200)
        except Exception as e:
            response_obj = {'status': 'failed', 'reason': str(e)}
            return web.Response(text=json.dumps(response_obj, indent=4), status=500)

async def exception_handler(request):
    raise NotImplementedError
