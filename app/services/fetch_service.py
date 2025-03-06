import httpx
import time
import redis.asyncio as redis
from sqlalchemy.orm import Session
from app import config
from app.models import Post, FetchJob
from app.schemas import PostCreate

CACHE_KEY = "last_fetch_timestamp"
FETCH_LOCK_KEY = "fetch_lock"  # Key used for the Redis lock

async def fetch_data_async(db: Session):
    redis_client = redis.from_url(
        f"redis://{config.REDIS_HOST}:{config.REDIS_PORT}",
        username=config.REDIS_USER,
        password=config.REDIS_PASSWORD,
        db=config.REDIS_DB,
        decode_responses=True
    )
    lock = redis_client.lock(FETCH_LOCK_KEY, timeout=30)
    acquired = await lock.acquire(blocking=False)
    if not acquired:
        return {"message": "Fetch in progress by another process", "status": "locked"}

    try:
        # Retrieve last_fetch_timestamp
        last_fetch_timestamp_str = await redis_client.get(CACHE_KEY)
        last_fetch_timestamp = float(last_fetch_timestamp_str) if last_fetch_timestamp_str else 0.0

        current_time = time.time()

        if current_time - last_fetch_timestamp < config.CACHE_EXPIRY_SECONDS:
            return {
                "message": "Fetch request ignored: within cache window",
                "status": "cached"
            }

        # Do your actual fetch
        async with httpx.AsyncClient() as client:
            resp = await client.get(config.EXTERNAL_API_URL)
            resp.raise_for_status()
            data = resp.json()

        # Update DB
        for item in data:
            post_create = PostCreate(**item)
            existing = db.query(Post).filter(Post.id == post_create.id).first()
            if existing:
                existing.title = post_create.title
                existing.body = post_create.body
                existing.user_id = post_create.userId
            else:
                new_post = Post(
                    id=post_create.id,
                    user_id=post_create.userId,
                    title=post_create.title,
                    body=post_create.body
                )
                db.add(new_post)

        db.commit()

        # Update timestamp in Redis
        await redis_client.set(CACHE_KEY, str(current_time))

        return {"message": "Data fetched successfully", "status": "ok"}
    finally:
        # Ensure we release the lock in all cases
        await lock.release()

def update_job_status(db: Session, job_id: int, job_error: str, status: str):
    job = db.query(FetchJob).filter(FetchJob.id == job_id).first()
    if job:
        job.status = status
        job.error = job_error
        db.commit()
        db.refresh(job)
    return job
