from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    title = Column(String)
    body = Column(String)

class FetchJob(Base):
    __tablename__ = "fetch_jobs"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="pending")  # e.g. pending, success, error
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    error = Column(String, default="")
