import asyncio

from celery.schedules import crontab
from sqlalchemy.orm import Session

from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.services.fetch_service import fetch_data_async, update_job_status
from app import config

@celery_app.task
def background_fetch_job(job_id: int):
    db: Session = SessionLocal()
    try:
        result = asyncio.run(fetch_data_async(db))
        if result["status"] == "ok":
            update_job_status(db, job_id, "", "success")
        else:
            update_job_status(db, job_id, result["message"], "error")
    finally:
        db.close()

# Setup periodic tasks (e.g., every 5 minutes)
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute=f'*/{config.BACKGROUND_FETCH_INTERVAL}'),
        periodic_fetch.s(),
        name="periodic-fetch"
    )

@celery_app.task
def periodic_fetch():
    """
    This task runs automatically every X minutes.
    We don't necessarily track it in a 'FetchJob' table, but you could if desired.
    """
    print("running periodic fetch")
    db: Session = SessionLocal()
    try:
        res = asyncio.run(fetch_data_async(db))  # ignoring the result for brevity
        print(f"res is {res}")
    finally:
        db.close()
