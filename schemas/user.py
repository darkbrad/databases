from pydantic import BaseModel
from typing import List


class UserDataModel(BaseModel):
    id: int
    login: str
    password: str
    folowers:int
    folowing:int


class UserDataResponseModel(BaseModel):
    id: int
    login: str
    folowers: int
    folowing: int


class RegistrationModel(BaseModel):
    username: str
    password: str

class BaseUserModel(BaseModel):
    id: str
    login: str

class UserModel(BaseUserModel):
    followers: int
    follows: int
class UserFollowModel(BaseModel):
    followers:List
    follows:List

