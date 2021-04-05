import base64
import bcrypt
from random import choice
import string
from app.base_models import ResponseResult
from abc import ABC, abstractmethod
import app.db as db
from datetime import datetime, timedelta

TOKEN_LIVE_HOURS = 2


class Credentials(ABC):
    '''Abstract credentials'''
    pass


class Authenticator(ABC):
    '''Abstract authenticator'''

    @abstractmethod
    def authenticate(self, credentials: Credentials) -> ResponseResult:
        pass


class Tokens(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Tokens, cls).__new__(cls)
            cls.__tokens_table = dict()
        return cls.instance

    def __get__(self, instance, owner):
        return self.__tokens_table


class Token:
    def __init__(self, token: str, user_id: int, login: str):
        self.expired = datetime.now() + timedelta(hours=TOKEN_LIVE_HOURS)
        self.token = token
        self.user_id = user_id
        self.login = login

    def is_alive(self) -> bool:
        return self.expired > datetime.now()

    def to_json(self):
        return {'token': self.token,
                'login': str(self.login),
                'expired': str(self.expired), }


class LoginCredentials(Credentials):
    '''Atributes for enter with login and password'''

    def __init__(self, login: str, password: str):
        self._login = login
        self._password = password

    @property
    def login(self) -> str:
        return self._login

    @property
    def password(self):
        return self._password


class LoginAuthennticator(Authenticator):
    async def authenticate(self, credentials: LoginCredentials) -> ResponseResult:
        user_response = await self.check_user_by_login(credentials.login)
        if not user_response.is_ok:
            return user_response
        df = await db.UsersTable().get_password_hash(credentials.login)
        if len(df) != 1:
            return ResponseResult(401, {'status': 'failed', 'reason': 'Password not found in DB'})
        db_password = df['password'][0]
        auth_ok = check_password_hash(db_password, credentials.password)
        if not auth_ok:
            return ResponseResult(401, {'status': 'failed', 'reason': 'Password incorrect'})
        token = create_new_user_token(user_response._response_obj['user_id'], credentials.login)
        response_result = ResponseResult(200, {'status': 'success', 'token': token})
        return response_result

    async def check_user_by_login(self, login) -> ResponseResult:
        result = await db.UsersTable().check_user_if_exists(login)
        if len(result) != 1:
            return ResponseResult(401, {'status': 'failed', 'reason': 'No user found'})
        user_id = int(result['user_id'][0])
        return ResponseResult(200, {'status': 'success', 'user_id': user_id, 'login': login})


async def authenticate(authenicator: Authenticator, credentials: Credentials) -> ResponseResult:
    return await authenicator().authenticate(credentials)


async def security_authenticate_by_login_password(login: str, password: str) -> ResponseResult:
    credentials = LoginCredentials(login, password)
    return await authenticate(LoginAuthennticator, credentials)


def create_new_user_token(user_id: int, login: str) -> Token:
    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    random_token = ''.join(choice(letters) for i in range(80))
    new_token = Token(random_token, user_id, login)

    # delete all previous user tokens
    old_user_tokens_list = []
    for token in Tokens().values():
        if token.user_id == user_id:
            old_user_tokens_list.append(token.token)
    for old_token in old_user_tokens_list:
        Tokens().pop(old_token, None)

    Tokens()[new_token.token] = new_token
    return new_token


def generate_password_hash(password: str) -> str:
    password_bin = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bin, bcrypt.gensalt())
    encoded = base64.b64encode(hashed)
    return encoded.decode('utf-8')


def check_password_hash(encoded: str, password: str) -> bool:
    password = password.encode('utf-8')
    encoded = encoded.encode('utf-8')
    hashed = base64.b64decode(encoded)
    is_correct = bcrypt.hashpw(password, hashed) == hashed
    return is_correct


def get_user_by_token(token_str: str) -> ResponseResult:
    if token_str not in Tokens():
        return ResponseResult(401, {'status': 'failed', 'reason': 'Unauthorized'})
    token = Tokens()[token_str]
    if not token.is_alive():
        return ResponseResult(401, {'status': 'failed', 'reason': 'Token expired'})
    return ResponseResult(200, {'status': 'success', 'token': token})
