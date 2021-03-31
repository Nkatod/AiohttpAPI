import db
import security
from abc import ABC, abstractmethod
from string import ascii_lowercase, ascii_uppercase, digits
from random import choice


class APIResponse(ABC):
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
    async def check_user_by_login(self) -> bool:
        result = await db.UsersTable.check_user_if_exists(self.login)
        if result is None:
            return False
        self.user_id = result
        return True

    async def is_exists(self) -> bool:
        return await self.check_user_by_login()

    def __init__(self, login, user_id=0, password=''):
        self.user_id = user_id
        self.login = login
        self.password = password
        self.token = None
        self.items = []

    def __eq__(self, other):
        return self.user_id == other.user_id

    def user_authorized(self) -> bool:
        if self.token is None:
            return False
        return self.token.is_alive()

    async def get_items(self):
        item_list = await db.ItemsTable().get_user_items(self.user_id)
        self.items = []
        for row in item_list:
            self.items.append(Item(item_id=row['item_id'], user=self, attribute=row['attr1']))

    async def find_item_by_id(self, item_id):
        if len(self.items) == 0:
            await self.get_items()
        for item in self.items:
            if item.item_id == item_id:
                return item
        return None

    def to_json(self):
        return {'user_id': self.user_id,
                'login': self.login}


class UserCreator(Creator):

    async def get_user_by_id(self, user_id: int) -> User:
        result = await db.UsersTable().get_login_by_id(user_id)
        if len(result) != 1:
            return User('')
        return User(result['login'][0])

    async def create_new_user(self, user_name: str, password: str) -> (ResponseResult, User):
        new_user = User(login=user_name)
        user_already_exists = await new_user.check_user_by_login()
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


class ReferenceToTransfer:
    def __init__(self, sender: User, receiver: User, item_to_move, reference=None):
        if reference is None:
            self.reference = self._generate_ref()
        else:
            self.reference = reference
        self.item_to_move = item_to_move
        self.sender = sender
        self.receiver = receiver
        self.response_status: ResponseResult = ResponseResult(500, {'status': 'failed',
                                                                    'reason': 'empty ReferenceToTransfer'})

    def _generate_ref(self):
        letters = ascii_lowercase + ascii_uppercase + digits
        random_token = ''.join(choice(letters) for _ in range(80))
        return random_token


class MovableToAnotherUserInterface(ABC):
    @abstractmethod
    async def create_reference_to_move(self, user_receiver: User) -> ReferenceToTransfer:
        pass

    @abstractmethod
    async def move_to_user(self, reference: ReferenceToTransfer) -> ResponseResult:
        pass


class Item(MovableToAnotherUserInterface):
    def __init__(self, item_id: int = None, user: User = None, attribute: str = None):
        self.item_id = item_id
        self.user = user
        self.attribute = attribute

    def __eq__(self, other):
        return self.item_id == other.item_id

    def to_json(self):
        return {'item_id': self.item_id,
                'attributes': self.attribute}

    async def delete_item(self) -> bool:
        item_result = await db.ItemsTable().delete_item(self.user.user_id, self.item_id)
        return item_result.rowcount > 0

    async def create_reference_to_move(self, user_receiver: User) -> ReferenceToTransfer:
        ref = ReferenceToTransfer(self.user, user_receiver, self)
        query_result = await db.ItemsTransportTable().create_send_to(ref.reference,
                                                                     user_receiver.user_id,
                                                                     self.user.user_id,
                                                                     self.item_id)
        if len(query_result) > 0:
            ref.response_status = ResponseResult(200, {'status': 'success', 'reference_for_accept': ref.reference})
        else:
            ref.response_status = ResponseResult(500, {'status': 'failed', 'reason': 'error adding new transfer in DB'})
        return ref

    async def move_to_user(self, ref: ReferenceToTransfer) -> ResponseResult:
        query_result = await db.ItemsTransportTable().move_to(ref.reference,
                                                              ref.receiver.user_id,
                                                              ref.sender.user_id,
                                                              ref.item_to_move.item_id)
        if len(query_result) != 1:
            return ResponseResult(500, {'status': 'failed', 'reason': 'error of object transfer in DB'})
        return ResponseResult(200, {'status': 'success'})


class ItemCreator(Creator):
    async def create_new_item(self, request) -> (ResponseResult, Item):
        token = str(request.query['token'])
        attributes = str(request.query['attributes'])
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
        token = str(request.query['token'])
        response_result, user = security.get_user_by_token(token)
        if response_result.status != 200:
            return response_result
        await user.get_items()

        item_found = False
        item_for_delete = None
        for item in user.items:
            if item.item_id == id_delete:
                item_found = True
                item_for_delete = item
                break

        if not item_found:
            return ResponseResult(500, {'status': 'failed',
                                        'reason': f'Item {str(id_delete)} not found for user {user.login}'})

        item_deleted = await item_for_delete.delete_item()
        if item_deleted:
            user.items.remove(item_for_delete)
            return ResponseResult(200, {'status': 'success'})
        else:
            return ResponseResult(500,
                                  {'status': 'failed', 'reason': f'cant delete item {str(id_delete)} : Internal error'})

    async def get_user_items(self, request) -> ResponseResult:
        token = str(request.query['token'])
        response_result, user = security.get_user_by_token(token)
        if response_result.status != 200:
            return response_result
        await user.get_items()
        items_list = []
        for val in user.items:
            items_list.append(val.to_json())
        return ResponseResult(200, {'status': 'success', 'items_list': items_list})

    async def send_item(self, request) -> ResponseResult:
        token = str(request.query['token'])
        receiver_login = str(request.query['login'])
        item_id = int(request.query['item_id'])

        # check user by token
        response_result, user = security.get_user_by_token(token)
        if response_result.status != 200:
            return response_result
        # find item_id in that user
        item_to_send = await user.find_item_by_id(item_id)
        if item_to_send is None:
            return ResponseResult(500, {'status': 'failed',
                                        'reason': f'Item {str(item_id)} not found for user {user.login}'})
        # find user receiver
        user_receiver = User(receiver_login)
        if not await user_receiver.is_exists():
            return ResponseResult(500, {'status': 'failed',
                                        'reason': f'User receiver {str(receiver_login)} not found'})

        # send item to user_receiver
        reference_to_move = await item_to_send.create_reference_to_move(user_receiver)
        return reference_to_move.response_status

    async def move_item(self, request) -> ResponseResult:
        token = str(request.query['token'])
        reference = str(request.query['reference'])

        # check user-receiver
        response_result, user_receiver = security.get_user_by_token(token)
        if response_result.status != 200:
            return response_result

        query_result = await db.ItemsTransportTable().get_transfer(reference, user_receiver.user_id)
        if len(query_result) == 0:
            return ResponseResult(500, {'status': 'failed',
                                        'reason': f'Reference {reference} '
                                                  f'not found for user receiver {str(user_receiver.user_id)}'})
        elif len(query_result) > 1:
            return ResponseResult(500, {'status': 'failed',
                                        'reason': f'Found many records for this reference'})
        # User sender should have this item
        user_sender_id = int(query_result['user_sender'][0])
        user_sender = await UserCreator().get_user_by_id(user_sender_id)
        if not await user_sender.is_exists():
            return ResponseResult(500, {'status': 'failed',
                                        'reason': f'User sender id {str(user_sender_id)} not found'})
        # find item_id in that user
        item_id = int(query_result['item_id'][0])
        item_to_send = await user_sender.find_item_by_id(item_id)
        if item_to_send is None:
            return ResponseResult(500, {'status': 'failed',
                                        'reason': f'Item {str(item_id)} not found for user {user_sender.login}'})
        ref = ReferenceToTransfer(sender=user_sender,
                                  receiver=user_receiver,
                                  item_to_move=item_to_send,
                                  reference=reference)
        response = await item_to_send.move_to_user(ref)
        return response


async def authenticate_by_login_password(login: str, password: str) -> (ResponseResult, User):
    return await security.authenticate_by_login_password(login, password)


async def get_all_users() -> list:
    users_list = []
    users_table = db.UsersTable()
    await users_table.get_all_users()
    for val in users_table.users_list:
        users_list.append(User(user_id=val['user_id'], login=val['login']).to_json())
    return users_list
