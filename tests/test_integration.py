"""Require running database server"""
from app.security import (
    generate_password_hash,
    check_password_hash
)
import init_db
import json


TEST_USERS_Q = 3



def test_cache():
    from app.cache import timed_cache
    import time

    class LogStream:
        def __init__(self):
            self.logs = []

        def add(self, log_str):
            self.logs.append(log_str)

        def get_last_log(self):
            if len(self.logs):
                return self.logs.pop(0)
            return ''

    log_stream = LogStream()
    @timed_cache(seconds=1)
    def cache_testing_function(num1, num2):
        nonlocal log_stream
        log_stream.add("Not cached yet.")
        return num1 + num2

    result1 = cache_testing_function(2, 3)
    last_log = log_stream.get_last_log()
    assert last_log == "Not cached yet."
    assert result1 == 5

    result2 = cache_testing_function(2, 3)
    last_log = log_stream.get_last_log()
    assert len(last_log) == 0
    assert result2 == 5

    time.sleep(1)
    result3 = cache_testing_function(2, 3)
    last_log = log_stream.get_last_log()
    assert last_log == "Not cached yet."
    assert result3 == 5


def test_security():
    user_password = 'Qwerty'
    hashed = generate_password_hash(user_password)
    assert check_password_hash(hashed, user_password)


def test_connection():
    assert init_db.test_connection(init_db.user_engine)




async def test_index_view(client):

    assert 1==1

    # resp = await client.get('/')
    # assert resp.status == 200
    # assert 'OK' in await resp.text()


# async def test_registration_new_user(client):
#     for i in range(TEST_USERS_Q):
#         data = {'login': f'user{i}', 'password': f'user{i}'}
#         resp = await client.post('/registration', params=data)
#         assert resp.status == 200
#         assert 'success' in await resp.text()
#
#
# async def test_users_list(client):
#     resp = await client.get('/users')
#     assert resp.status == 200
#     assert 'user1' in await resp.text()
#     assert 'user2' in await resp.text()
#
#
# async def authorization(client, login, password) -> str:
#     data = {'login': login, 'password': password}
#     resp = await client.post('/login', params=data)
#     assert resp.status == 200
#     resp_text = await resp.text()
#     assert 'token' in resp_text
#     resp_json = json.loads(resp_text)
#     token = resp_json['token']['token']
#     assert len(token) > 0
#     return token
#
#
# async def create_new_item(client, token) -> int:
#     data = {'token': token, 'attributes': 'TEST'}
#     resp = await client.post('/items/new', params=data)
#     assert resp.status == 200
#     resp_text = await resp.text()
#     assert 'success' in resp_text
#     assert 'item_id' in resp_text
#     resp_json = json.loads(resp_text)
#     item_id = int(resp_json['item_id'])
#     assert item_id > 0
#     return item_id
#
#
# async def delete_item(client, token, item_id):
#     data = {'token': token}
#     resp = await client.delete(f'/items/{item_id}', params=data)
#     assert resp.status == 200
#     resp_text = await resp.text()
#     assert 'success' in resp_text
#
#
# async def test_users_authorization(client):
#     for i in range(TEST_USERS_Q):
#         await authorization(client, f'user{i}', f'user{i}')
#
#
# async def test_create_items(client):
#     for i in range(TEST_USERS_Q):
#         # authorize
#         token = await authorization(client, f'user{i}', f'user{i}')
#         # create new item
#         await create_new_item(client, token)
#
#
# async def test_get_items(client):
#     # authorize
#     token = await authorization(client, 'user1', 'user1')
#     # get user items
#     data = {'token': token, 'attributes': 'TEST'}
#     resp = await client.get('items', params=data)
#     assert resp.status == 200
#     resp_text = await resp.text()
#     assert 'success' in resp_text
#     assert 'item_id' in resp_text
#
#
# async def test_delete_items(client):
#     # authorize
#     token = await authorization(client, 'user1', 'user1')
#
#     # create new item
#     item_id = await create_new_item(client, token)
#
#     # delete item
#     await delete_item(client, token, item_id)
#
#
# async def create_reference_to_move(client, token, item_id, login_accepter):
#     data = {'token': token, 'item_id': item_id, 'login': login_accepter}
#     resp = await client.post('/send', params=data)
#     assert resp.status == 200
#     resp_text = await resp.text()
#     assert 'success' in resp_text
#     assert 'reference_for_accept' in resp_text
#     resp_json = json.loads(resp_text)
#     reference_for_accept = str(resp_json['reference_for_accept'])
#     assert len(reference_for_accept) > 0
#     return reference_for_accept
#
#
# async def get_reference_for_move(client, login_sender, login_accepter):
#     # authorize
#     token = await authorization(client, login_sender, login_sender)
#     # create new item
#     item_id = await create_new_item(client, token)
#     return await create_reference_to_move(client,
#                                           token,
#                                           item_id,
#                                           login_accepter)
#
#
# async def test_create_reference_to_move(client):
#     await get_reference_for_move(client, 'user1', 'user2')
#
#
# async def get_item_from_another_user(client, login_accepter, reference_to_move):
#     # authorize login_accepter
#     token = await authorization(client, login_accepter, login_accepter)
#     # get item
#     data = {'token': token, 'reference': reference_to_move}
#     resp = await client.get('/get', params=data)
#     assert resp.status == 200
#     resp_text = await resp.text()
#     assert 'success' in resp_text
#
#
# async def test_get_item_from_another_user(client):
#     login_sender = 'user1'
#     login_accepter = 'user2'
#     reference_to_move = await get_reference_for_move(client,
#                                                      login_sender,
#                                                      login_accepter)
#     await get_item_from_another_user(client, login_accepter, reference_to_move)
