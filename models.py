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
        self.items = []

    def user_authorized(self) -> bool:
        if self.token is None:
            return False
        return self.token.is_alive()

    async def get_items(self):
        item_list = await db.ItemsTable().get_user_items(self.user_id)
        self.items = []
        for row in item_list:
            self.items.append(Item(item_id=row['item_id'], user=self, attribute=row['attr1']))


    def to_json(self):
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
    def __init__(self, item_id: int = None, user: User = None, attribute: str = None):
        self.item_id = item_id
        self.user = user
        self.attribute = attribute

    def to_json(self):
        return {'item_id': self.item_id,
                'attributes': self.attribute}

    async def delete_item(self) -> bool:
        item_result = await db.ItemsTable().delete_item(self.user.user_id, self.item_id)
        return item_result.rowcount > 0


class ItemCreator(Creator):
    async def create_new_item(self, request) -> (ResponseResult, Item):
        token = request.query['token']
        attributes = request.query['attributes']
        response_result, user = security.get_user_by_token(token)
        if response_result.status != 200:
            return response_result, Item()
        item_result = await db.ItemsTable().create_new_item(user.user_id, attributes)
        if item_result.rowcount != 1:
            return ResponseResult(500, {'status': 'failed', 'reason': 'error adding new item'}), Item()
        new_item = Item(item_id=item_result.lastrowid, user=user, attribute=attributes)
        response_result = ResponseResult(200,
                                         {'status': 'success',
                                          'item_id': new_item.item_id,
                                          'attributes': new_item.attribute, })
        return response_result, new_item

    async def delete_item(self, request) -> ResponseResult:
        id_delete = int(request.match_info['item_id'])
        token = request.query['token']
        response_result, user = security.get_user_by_token(token)
        if response_result.status != 200:
            return response_result
        await user.get_items()

        item_found = False
        for item in user.items:
            if item.item_id == id_delete:
                item_found = True
                break

        if not item_found:
            return ResponseResult(500, {'status': 'failed', 'reason': f'Item {str(id_delete)} not found for user {user.login}'})

        item_deleted = await item.delete_item()
        if item_deleted:
            user.items.remove(item)
            return ResponseResult(200, {'status': 'success'})
        else:
            return ResponseResult(500, {'status': 'failed', 'reason': f'cant delete item {item.item_id} : Internal error'})


async def authenticate_by_login_password(login: str, password: str) -> (ResponseResult, User):
    return await security.authenticate_by_login_password(login, password)


async def get_all_users() -> list:
    users_list = []
    users_table = db.UsersTable()
    await users_table.get_all_users()
    for val in users_table.users_list:
        users_list.append(User(user_id=val['user_id'], login=val['login']).toJson())
    return users_list
