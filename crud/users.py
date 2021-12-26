import sqlite3
from werkzeug.exceptions import HTTPException
from pydantic import BaseModel
from schemas.user import UserDataModel,BaseUserModel,UserFollowModel,RegistrationModel,UserModel
from typing import Dict as dict
from werkzeug.datastructures import Authorization
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

    def get(self, conn: sqlite3.Connection, login: str) -> UserModel:
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
            user = self.get(conn, data.username)
            if user is not None:
                raise UserExistsError(f"User with login {data.username} already exists")

            user_id = uuid.uuid4()
            cur.execute(
                "INSERT INTO User VALUES(?, ?, ?,?,?)",
                (str(user_id), data.username, passwords.hash_password(data.password),0,0),
            )
        finally:
            cur.close()

    def authenticate(
            self, conn: sqlite3.Connection, auth_data: Authorization
    ) -> UserModel:
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT password FROM User WHERE login=?", (auth_data.username,)
            )
            row = cur.fetchone()

            if row is None:
                raise AuthError("User does not exist")

            password_hashed = row[0]

            if not passwords.passwords_equal(auth_data.password, password_hashed):
                raise AuthError("Password is incorrect")

            assert auth_data.username is not None

            return self.get(conn, auth_data.username)
        finally:
            cur.close()

    def get_followers_and_follows(
            self, conn: sqlite3.Connection, user:BaseUserModel
    ) ->UserFollowModel :
        cur = conn.cursor()

        try:
            cur.execute(
                "SELECT follows "
                "FROM Follow "
                "WHERE follower=? "
                "",
                (user.id,),
            )
            data_of_follows = cur.fetchall()

            cur.execute("SELECT follower "
                        "FROM Follow "
                        "WHERE follows=? ",(user.id,),)
            data_of_followers=cur.fetchall()

            return UserFollowModel(followers=data_of_followers,follows=data_of_follows)
        finally:
            cur.close()

