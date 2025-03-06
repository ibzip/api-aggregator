import os

EXTERNAL_API_URL = "https://jsonplaceholder.typicode.com/posts"
CACHE_EXPIRY_SECONDS = 60
# RabbitMQ broker URL (assuming default credentials and Docker Compose naming)
CELERY_BROKER_URL = "amqp://guest:guest@rabbitmq:5672//"
CELERY_RESULT_BACKEND = "rpc://"
BACKGROUND_FETCH_INTERVAL = 3 # minutes

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")    # default 'redis' if running in docker
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))  # default Redis port
REDIS_DB = int(os.environ.get("REDIS_DB", 0))         # default DB index
REDIS_USER = os.environ.get("REDIS_USER", None)       # Typically not used unless ACL is configured
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)  # Usually no password by