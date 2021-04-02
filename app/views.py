import app.models as models
from aiohttp import web
import json


async def handle(request):
    """
        ---
        description: This end-point allow to test that service is up.
        tags:
        - Health check
        produces:
        - application/json
        responses:
            "200":
                description: successful operation.
    """

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
        """
            ---
            summary: Get all users list
            description: Get all users list
            tags:
            - User
            produces:
            - application/json
            responses:
                "200":
                    description: successful operation.
                "500":
                    description: Internal server error
        """
        try:
            users_list = await models.get_all_users()
            response_obj = {'status': 'success', 'users_list': users_list}
            return web.Response(text=json.dumps(response_obj, indent=4), status=200)
        except Exception as e:
            response_obj = {'status': 'failed', 'reason': str(e)}
            return web.Response(text=json.dumps(response_obj, indent=4), status=500)

    @staticmethod
    async def authorization(request):
        """
            ---
            summary: Authorize user
            description: This end-point allow to authorize user
            tags:
            - User
            produces:
            - application/json
            parameters:
            - in: query
              name: login
              description: login
              required: true
              default: user1
              type: string
            - in: query
              name: password
              description: login
              required: true
              default: password
              type: string
            responses:
            "200":
                description: successful operation
            "401":
                description: Unauthorized
            "500":
                description: Internal server error
        """
        try:
            response_result = await models.authenticate_by_login_password(request)
            if response_result.is_ok:
                response_result.response_obj['token'] = response_result.response_obj['token'].to_json()
            return web.Response(text=json.dumps(response_result.response_obj, indent=4), status=response_result.status)
        except Exception as e:
            response_obj = {'status': 'failed', 'reason': str(e)}
            return web.Response(text=json.dumps(response_obj, indent=4), status=500)


class ItemsView:
    @staticmethod
    async def create_new_item(request):
        try:
            response_result = await models.ItemCreator().create_new_item(request)
            return web.Response(text=json.dumps(response_result.response_obj, indent=4), status=response_result.status)
        except Exception as e:
            response_obj = {'status': 'failed', 'reason': str(e)}
            return web.Response(text=json.dumps(response_obj, indent=4), status=500)

    @staticmethod
    async def delete_item(request):
        try:
            response_result = await models.ItemCreator().delete_item(request)
            return web.Response(text=json.dumps(response_result.response_obj, indent=4), status=response_result.status)
        except Exception as e:
            response_obj = {'status': 'failed', 'reason': str(e)}
            return web.Response(text=json.dumps(response_obj, indent=4), status=500)

    @staticmethod
    async def get_user_items(request):
        try:
            response_result = await models.ItemCreator().get_user_items(request)
            return web.Response(text=json.dumps(response_result.response_obj, indent=4), status=response_result.status)
        except Exception as e:
            response_obj = {'status': 'failed', 'reason': str(e)}
            return web.Response(text=json.dumps(response_obj, indent=4), status=500)

    @staticmethod
    async def send_item(request):
        try:
            response_result = await models.ItemCreator().send_item(request)
            return web.Response(text=json.dumps(response_result.response_obj, indent=4), status=response_result.status)
        except Exception as e:
            response_obj = {'status': 'failed', 'reason': str(e)}
            return web.Response(text=json.dumps(response_obj, indent=4), status=500)

    @staticmethod
    async def move_item(request):
        try:
            response_result = await models.ItemCreator().move_item(request)
            return web.Response(text=json.dumps(response_result.response_obj, indent=4), status=response_result.status)
        except Exception as e:
            response_obj = {'status': 'failed', 'reason': str(e)}
            return web.Response(text=json.dumps(response_obj, indent=4), status=500)


async def exception_handler(request):
    raise NotImplementedError
