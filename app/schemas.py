from pydantic import BaseModel
from datetime import datetime

class PostCreate(BaseModel):
    userId: int
    id: int
    title: str
    body: str

class PostResponse(BaseModel):
    user_id: int
    id: int
    title: str
    body: str

    class Config:
        orm_mode = True

class FetchJobStatus(BaseModel):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    error: str

    class Config:
        orm_mode = True
