import base64
import functools

import bcrypt
from aiohttp import web
from aiohttp_security import authorized_userid
from aiohttp_security.abc import AbstractAuthorizationPolicy
from random import choice
import string


def create_new_user_token(user_id) -> str:
    letters = string.ascii_lowercase + string.ascii_uppercase
    a = ''.join(choice(letters) for i in range(80))
    #TODO запомнить в кэш
    return a

def generate_password_hash(password: str, salt_rounds=12) -> str:
    password_bin = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bin, bcrypt.gensalt(salt_rounds))
    encoded = base64.b64encode(hashed)
    return encoded.decode('utf-8')


def check_password_hash(encoded: str, password: str) -> bool:
    password = password.encode('utf-8')
    encoded = encoded.encode('utf-8')

    hashed = base64.b64decode(encoded)
    is_correct = bcrypt.hashpw(password, hashed) == hashed
    return is_correct


class AuthorizationPolicy(AbstractAuthorizationPolicy):
    def __init__(self, mongo):
        self.mongo = mongo

    async def authorized_userid(self, identity):
        user = await self.mongo.user.find_one({'_id': ObjectId(identity)})
        if user:
            return identity
        return None

    async def permits(self, identity, permission, context=None):
        if identity is None:
            return False
        return True


def auth_required(f):
    @functools.wraps(f)
    async def wrapped(self, request):
        user_id = await authorized_userid(request)
        if not user_id:
            raise web.HTTPUnauthorized()
        return (await f(self, request))

    return wrapped
