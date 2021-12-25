from flask import request
from crud import user_crud
from core.db import get_connection
from core import errors
from schemas.user import UserModel
from pydantic import BaseModel


def get_current_user() -> UserModel:
    auth_data = request.authorization
    if auth_data is None:
        raise errors.AuthError("Auth headers not provided")

    with get_connection() as conn:
        user_data = user_crud.authenticate(conn, auth_data)

    return user_data


def get_user_by_login(login: str) -> UserModel:
    with get_connection() as conn:
        user_data = user_crud.get(conn, login)

    if user_data is None:
        raise errors.NotFoundError(f"User with login '{login}' was not found")

    return user_data


def get_input(ModelType) -> BaseModel:
    data = request.get_json(True)
    if data is None:
        raise errors.InvalidDataFormat("Json not found")

    return ModelType(**data)