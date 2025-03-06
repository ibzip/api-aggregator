from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Post, FetchJob
from app.schemas import PostResponse, FetchJobStatus

router = APIRouter()

@router.get("/data", response_model=List[PostResponse])
def get_data(user_id: Optional[int] = None, db: Session = Depends(get_db)):
    """
    Retrieve posts. Optional filter: /data?user_id=1
    """
    query = db.query(Post)
    if user_id is not None:
        query = query.filter(Post.user_id == user_id)
    return query.all()

@router.get("/fetch/status/{job_id}", response_model=FetchJobStatus)
def get_fetch_job_status(job_id: int, db: Session = Depends(get_db)):
    """
    Poll the status of a fetch job by its ID.
    Returns 404 if the job does not exist.
    """
    job = db.query(FetchJob).filter(FetchJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Because we've enabled `orm_mode = True` in FetchJobStatus,
    # we can directly return the SQLAlchemy model object.
    return job
