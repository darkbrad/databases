import sqlite3
from werkzeug.exceptions import HTTPException
from pydantic import BaseModel
from schemas.user import UserDataModel
from typing import Dict as dict
from schemas.user import BaseUserModel,UserFollowModel,RegistrationModel,UserModel
import uuid
from core import passwords
from core.errors.auth_errors import AuthError
from core.errors.registration_errors import UserExistsError

class UserStorageModel(BaseModel):
    user_data: dict[str, UserDataModel]


class AuthError(HTTPException):
    code = 401
    description = "Authorization error"


class RegistrationError(HTTPException):
    code = 409
    description = "Registration error"


class UserCRUD:
    data: UserStorageModel

    def get_user_data(self, conn: sqlite3.Connection, login: str) -> UserModel:
        cur = conn.cursor()

        try:
            cur.execute(
                "SELECT User.id, User.login, "
                " COUNT(DISTINCT f1.follower), COUNT(DISTINCT f2.follows)"
                "FROM User "
                "LEFT JOIN Follow AS f1 ON f1.follows = User.id "
                "LEFT JOIN Follow AS f2 ON f2.follower = User.id "
                "WHERE User.login=?",
                (login,),
            )
            row = cur.fetchone()

            if row is None:
                return None

            id, login, followers, follows = row

            if id is None:
                return None

            return UserModel(id=id, login=login, followers=followers, follows=follows)
        finally:
            cur.close()

    def create(self, conn: sqlite3.Connection, data: RegistrationModel) -> None:
        cur = conn.cursor()

        try:
            user = self.get(conn, data.login)
            if user is not None:
                raise UserExistsError(f"User with login {data.login} already exists")

            user_id = uuid.uuid4()
            cur.execute(
                "INSERT INTO User VALUES(?, ?, ?)",
                (str(user_id), data.login, passwords.hash_password(data.password)),
            )
        finally:
            cur.close()


    def authenticate(self, username: str, password: str,) -> UserDataModel:
        """
        Authenticate a user based on his username or password.
        In case of an error, raises AuthError.
        """

        user_data = self.get_user_data(username)
        if user_data is None:
            raise AuthError(f"User with name {username} does not exist")

        if not passwords.passwords_equal(password, user_data.password):
            raise AuthError(f"Password for user {username} is not correct")

        return user_data

    def get_followers_and_follows(
            self, conn: sqlite3.Connection, user:BaseUserModel
    ) ->UserFollowModel :
        cur = conn.cursor()

        try:
            cur.execute(
                "SELECT follows"
                "FROM Follow "
                "WHERE follower=? "
                "",
                (user.id,),
            )
            data_of_follows = cur.fetchall()

            cur.execute("SELECT follower"
                        "FROM Follow"
                        "WHERE follows=? ",(user.id,),)
            data_of_followers=cur.fetchall()

            return UserFollowModel(followers=data_of_followers,follows=data_of_follows)
        finally:
            cur.close()

