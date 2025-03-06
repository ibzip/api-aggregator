from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import FetchJob
from app.services.fetch_service import fetch_data_async
from app.tasks.tasks import background_fetch_job

router = APIRouter()

@router.post("/fetch")
async def fetch_data(mode: str = "sync", db: Session = Depends(get_db)):
    """
    1) mode=task:
       Enqueue a background Celery task (fetch_data_async called by Celery worker).
       Return a job_id to track status.
    2) mode=sync (default):
       Call fetch_data_async right in this request, returning success/failure immediately.
    """

    if mode == "task":
        new_job = FetchJob(status="pending")
        db.add(new_job)
        db.commit()
        db.refresh(new_job)

        background_fetch_job.delay(new_job.id)
        return {
            "message": "Fetch job queued in background",
            "job_id": new_job.id
        }

    else:
        # mode=sync => call fetch_data_async directly
        fetch_result = await fetch_data_async(db)
        return fetch_result
