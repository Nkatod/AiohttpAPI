<<<<<<< HEAD
import db


class User:
    async def is_exists(self, user_name) -> bool:
        return await self.check_user_if_exists(user_name)

    @staticmethod
    async def check_user_if_exists(user_name) -> bool:
        return await db.UsersTable.check_user_if_exists(user_name)

    def __init__(self, user_id, login, password):
        self.user_id = user_id
        self.login = login
        self.password = password


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
=======
import db


class User:
    async def is_exists(self, user_name) -> bool:
        return await self.check_user_if_exists(user_name)

    @staticmethod
    async def check_user_if_exists(user_name) -> bool:
        return await db.UsersTable.check_user_if_exists(user_name)

    def __init__(self, user_id, login, password):
        self.user_id = user_id
        self.login = login
        self.password = password


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
>>>>>>> 4b0356d9b8929b4372a010fce368bc581a064d8f
