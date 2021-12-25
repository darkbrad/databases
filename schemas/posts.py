from pydantic import BaseModel, Field
from datetime import datetime
from .user import BaseUserModel
import uuid


class ReturnPostModel(BaseModel):
    id: str
    creator: BaseUserModel
    description: str
    created: datetime


class BaseCreatePostModel(BaseModel):
    description: str


class CreatePostModel(BaseCreatePostModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str
    created: datetime = Field(default_factory=datetime.now)