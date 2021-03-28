import base64
import bcrypt
from random import choice
import string
from models import User, ResponseResult
from abc import ABC, abstractmethod
import db
from datetime import datetime, timedelta

TOKEN_LIVE_HOURS = 2


class Credentials(ABC):
    '''Abstract credentials'''
    pass


class Authenticator(ABC):
    '''Abstract authenticator'''

    @abstractmethod
    def authenticate(self, credentials: Credentials) -> (ResponseResult, User):
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
    def __init__(self, token: str, user: User):
        self.expired = datetime.now() + timedelta(hours=TOKEN_LIVE_HOURS)
        self.token = token
        self.user = user

    def is_alive(self) -> bool:
        return self.expired > datetime.now()

    def toJson(self):
        return {'token': self.token,
                'login': str(self.user.login),
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
    async def authenticate(self, credentials: LoginCredentials) -> (ResponseResult, User):
        curr_user = User(login=credentials.login)
        if not await curr_user.is_exists():
            return ResponseResult(401, {'status': 'failed', 'reason': 'No user found'}), curr_user
        db_password = await db.UsersTable.get_password_hash(credentials.login)
        auth_ok = check_password_hash(db_password, credentials.password)
        if not auth_ok:
            return ResponseResult(401, {'status': 'failed', 'reason': 'Password incorrect'}), curr_user
        response_result = ResponseResult(200, {'status': 'success'})
        curr_user.token = create_new_user_token(curr_user)
        return response_result, curr_user


async def authenticate(authenicator: Authenticator, credentials: Credentials) -> (ResponseResult, User):
    return await authenicator().authenticate(credentials)


async def authenticate_by_login_password(login: str, password: str) -> (ResponseResult, User):
    credentials = LoginCredentials(login, password)
    return await authenticate(LoginAuthennticator, credentials)


def create_new_user_token(user: User) -> Token:
    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    random_token = ''.join(choice(letters) for i in range(80))
    new_token = Token(random_token, user)
    Tokens()[new_token.token] = new_token
    return new_token


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

def get_user_by_token(token_str:str)-> (ResponseResult, User):
    if not token_str in Tokens():
        return ResponseResult(401, {'status': 'failed', 'reason': 'Unauthorized'}), User(None)
    token = Tokens()[token_str]
    if not token.is_alive():
        return ResponseResult(401, {'status': 'failed', 'reason': 'Token expired'}), token.user

    return ResponseResult(200, {'status': 'success', }), token.user
