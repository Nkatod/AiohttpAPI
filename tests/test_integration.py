"""Require running database server"""
from app.security import (
    generate_password_hash,
    check_password_hash
)
import init_db


def test_security():
    user_password = 'Qwerty'
    hashed = generate_password_hash(user_password)
    assert check_password_hash(hashed, user_password)


def test_connection():
    assert init_db.test_connection(init_db.user_engine)


async def test_index_view(client):
    resp = await client.get('/')
    assert resp.status == 200
    assert 'OK' in await resp.text()


async def test_registration_new_user(client):
    for i in range(10):
        data = {'login': f'user{i}', 'password': f'user{i}'}
        resp = await client.post('/registration', params=data)
        assert resp.status == 200
        assert 'success' in await resp.text()
