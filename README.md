# API aggregator backend

This is a backend solution for the API Aggregator coding challenge. It demonstrates:

- A **FastAPI** application fetching data from an external API and storing it in an SQLite database.
- Asynchronous operations and background tasks with **Celery + RabbitMQ**.
- Periodic background fetching tasks.
- Unit and integration tests with **pytest**.

## Table of Contents

1. [Requirements](#requirements)
2. [Project Structure](#project-structure)
3. [Installation](#installation)
4. [Running the Project](#running-the-project)
   - [Using Docker Compose](#using-docker-compose)
5. [Testing](#testing)
6. [API Endpoints](#api-endpoints)
7. [Troubleshooting](#troubleshooting)

---

## Requirements

- Python 3.10 or 3.11
- Docker & Docker Compose

---

## Project Structure

```
code_dir/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── routers/
│   │   ├── fetch.py
│   │   ├── data.py
│   │   └── job_status.py
│   ├── services/
│   │   └── fetch_service.py
│   ├── tasks/
│   │   ├── celery_app.py
│   │   └── tasks.py
│   └── tests/
│       └── test_routes.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Installation

**Locally (without Docker)**:

```bash
git clone <your-repo-url>
cd <repo-name>

python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

pip install --upgrade pip
pip install -r requirements.txt
```

---

## Running the Project

### Using Docker Compose

**Build and start all services:**

```bash
docker-compose build
docker-compose up
```

This starts:

- `aggregator_app`: FastAPI (port 8000)
- `rabbitmq`: RabbitMQ broker (port 5672, UI on 15672)
- `celery_worker`: background tasks
- `celery_beat`: periodic task scheduler

API documentation at:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Testing

Tests are written using **pytest**.

**Running tests locally:**

```bash
pytest app/tests -v
```

**Running tests in Docker:**

```bash
docker-compose run aggregator_app pytest app/tests -v
```

---

## API Endpoints

### Trigger Data Fetch

- **Immediate Fetch (synchronous)**:

```bash
curl -X POST "http://localhost:8000/fetch?mode=sync"
```

- **Background Fetch (Celery task)**:

```bash
curl -X POST "http://localhost:8000/fetch?mode=task"
```

### Check Fetch Job Status

Replace `{job_id}` with your actual job ID:

```bash
curl "http://localhost:8000/fetch/status/{job_id}"
```

### Retrieve Stored Data

- Retrieve all posts:

```bash
curl "http://localhost:8000/data"
```

- Filter posts by `user_id`:

```bash
curl "http://localhost:8000/data?user_id=1"
```

---

## Troubleshooting

- **RabbitMQ Connection Issues:**
  - Ensure RabbitMQ is running.
  - Docker uses hostname `rabbitmq`. Locally, use `localhost`.

- **Database**:
  - SQLite DB (`aggeragator.db`) is created in the project root.

- **Celery Tasks**:
  - Verify Celery worker logs:

```bash
docker-compose logs celery_worker
```

- Confirm tasks are imported correctly (`celery_app.conf.imports`).

---

## License

MIT License