import db
from security import check_password_hash, create_new_user_token


class User:
    async def is_exists(self) -> bool:
        if len(self.login) == 0:
            raise ValueError('login is empty')
        result = await db.UsersTable.check_user_if_exists(self.login)
        if result is None:
            return False
        self.user_id = result
        return True

    async def authorize(self, password:str) -> bool:
        if len(self.login) == 0:
            raise ValueError('login is empty')
        db_password = await db.UsersTable.get_password_hash(self.login)
        return check_password_hash(db_password, password)

    def create_new_user_token(self):
        self.token = create_new_user_token(self.user_id)

    def __init__(self, login, user_id=0, password=''):
        self.user_id = user_id
        self.login = login
        self.password = password
        self.token = None

    def toJson(self):
        return {'user_id': self.user_id,
                'login': self.login}


class UserCreator:
    @staticmethod
    async def create_new_user(user_name, password):
        new_user = User(login=user_name)
        user_already_exists = await new_user.is_exists()
        if user_already_exists:
            raise ValueError('this login has already existed!')
        user_result = await db.UsersTable.create_new_user(user_name, password)
        if user_result.rowcount != 1:
            raise ValueError('error adding new user')
        return User(user_id=user_result.lastrowid, login=user_name, password=password)

    @staticmethod
    async def get_all_users():
        users_list = []
        users_table = db.UsersTable()
        await users_table.get_all_users()
        for val in users_table.users_list:
            users_list.append(User(user_id=val['user_id'], login=val['login']).toJson())
        return users_list
