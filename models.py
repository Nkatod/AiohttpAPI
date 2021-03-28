import db
import security
from abc import ABC, abstractmethod


class APIResponse(ABC):
    '''API response'''
    pass


class Creator(ABC):
    pass


class ResponseResult(APIResponse):
    def __init__(self, status_number: int, response_obj: dict):
        self._status = status_number
        self._response_obj = response_obj

    @property
    def response_obj(self):
        return self._response_obj

    @property
    def status(self):
        return self._status


class User:
    async def is_exists(self) -> bool:
        if len(self.login) == 0:
            raise ValueError('login is empty')
        result = await db.UsersTable.check_user_if_exists(self.login)
        if result is None:
            return False
        self.user_id = result
        return True

    def __init__(self, login, user_id=0, password=''):
        self.user_id = user_id
        self.login = login
        self.password = password
        self.token = None

    def user_authorized(self) -> bool:
        if self.token is None:
            return False
        return self.token.is_alive()

    def toJson(self):
        return {'user_id': self.user_id,
                'login': self.login}


class UserCreator(Creator):
    async def create_new_user(self, user_name: str, password: str) -> (ResponseResult, User):
        new_user = User(login=user_name)
        user_already_exists = await new_user.is_exists()
        if user_already_exists:
            response_result = ResponseResult(500, {'status': 'failed', 'reason': 'this login has already existed!'})
            return response_result, new_user
        user_result = await db.UsersTable.create_new_user(user_name, password)
        if user_result.rowcount != 1:
            response_result = ResponseResult(500, {'status': 'failed', 'reason': 'error adding new user'})
            return response_result, new_user
        new_user = User(user_id=user_result.lastrowid, login=user_name, password=password)
        response_result = ResponseResult(200,
                                         {'status': 'success',
                                          'user_id': new_user.user_id,
                                          'user': new_user.login,
                                          'password': new_user.password})
        return response_result, new_user


class Item:
    def __init__(self):
        pass


class ItemCreator(Creator):
    async def create_new_item(self, request) -> (ResponseResult, Item):
        token = request.query['token']
        attributes = request.query['attributes']
        response_result, user = security.get_user_by_token(token)
        if response_result.status != 200:
            return response_result, Item()
        return response_result, Item()


async def authenticate_by_login_password(login: str, password: str) -> (ResponseResult, User):
    return await security.authenticate_by_login_password(login, password)


async def get_all_users() -> list:
    users_list = []
    users_table = db.UsersTable()
    await users_table.get_all_users()
    for val in users_table.users_list:
        users_list.append(User(user_id=val['user_id'], login=val['login']).toJson())
    return users_list
