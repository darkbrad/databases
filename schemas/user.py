from pydantic import BaseModel, Field, validator
from typing import List


class UserDataModel(BaseModel):
    id: int
    login: str
    password: str
    folowers:int
    folowing:int


class UserDataResponseModel(BaseModel):
    id: str
    login: str
    folowers: int
    folowing: int


class RegistrationModel(BaseModel):
    username: str = Field(min_length=6)
    password: str = Field(min_length=8)

    @validator("username")
    def validate_login(cls, username: str) -> str:
        assert " " not in username, "No spaces allowed in login"
        return username

class BaseUserModel(BaseModel):
    id: str
    login: str

class UserModel(BaseUserModel):
    followers: int
    follows: int
class UserFollowModel(BaseModel):
    followers:List
    follows:List

