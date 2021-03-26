import db

class User:
    async def is_exists(self, user_name) -> bool:
        return await self.check_user_if_exists(user_name)

    @staticmethod
    async def check_user_if_exists(user_name) -> bool:
        return await db.UsersTable.check_user_if_exists(user_name)

    def __init__(self, user_id, login, password=''):
        self.user_id = user_id
        self.login = login
        self.password = password

    def toJson(self):
        return {'user_id': self.user_id,
                'login': self.login}


class UserCreator:
    @staticmethod
    async def create_new_user(user_name, password):
        user_already_exists = await User.check_user_if_exists(user_name)
        if user_already_exists:
            raise ValueError('this login has already existed!')
        user_result = await db.UsersTable.create_new_user(user_name, password)
        if user_result.rowcount != 1:
            raise ValueError('error adding new user')
        return User(user_result.lastrowid, user_name, password)

    @staticmethod
    async def get_all_users():
        users_list = []
        users_table = db.UsersTable()
        await users_table.get_all_users()
        for val in users_table.users_list:
            users_list.append(User(val['user_id'], val['login']).toJson())
        return users_list
