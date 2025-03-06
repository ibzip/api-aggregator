# Architecture Explanation

## Overview

The VESTIGAS backend application is designed with a modern, asynchronous architecture focused on scalability, performance, and maintainability. It employs FastAPI as the web framework, Celery with RabbitMQ for asynchronous and periodic task management, and SQLite for database persistence.

## Components

### 1. Web Layer (FastAPI)

The FastAPI web layer exposes REST API endpoints allowing users to:

- Trigger synchronous or asynchronous data fetching.
- Check the status of background tasks.
- Retrieve data stored in the SQLite database.

The endpoints are defined clearly and documented automatically using OpenAPI (Swagger UI and ReDoc).

### 2. Database Layer (SQLite)

SQLite stores fetched data persistently and manages fetch-job statuses. SQLAlchemy ORM abstracts database interactions, enabling easy migration to more robust databases (e.g., PostgreSQL).

### 3. Background Task Processing (Celery + RabbitMQ)

Celery, combined with RabbitMQ, handles asynchronous tasks:

- **Celery Workers** perform tasks in the background without blocking the API.
- **Celery Beat** schedules periodic tasks, such as automatic data fetching at regular intervals.

### 4. Task Scheduling & Execution

- Celery Beat periodically schedules fetch tasks.
- Tasks can also be explicitly triggered by API requests.

### 5. External API Integration

FastAPI endpoints or Celery tasks asynchronously fetch data from an external API (e.g., JSONPlaceholder). This data is then parsed and stored within the SQLite database.

## Workflow

### Synchronous Data Fetching (Immediate):

1. User makes a synchronous fetch request to the API (`/fetch?mode=sync`).
2. FastAPI calls the external API asynchronously, waits for the response, and stores data directly in SQLite.
3. User receives immediate feedback regarding the success or failure of the operation.

### Asynchronous Data Fetching (Background Tasks):

1. User triggers asynchronous fetching (`/fetch?mode=task`).
2. FastAPI inserts a new fetch-job record into SQLite with a status of "pending".
3. FastAPI enqueues a fetch task into Celery (via RabbitMQ).
4. Celery workers process the task independently, updating the database status to "success" or "error" accordingly.
5. User polls the job status using the provided `job_id`.

### Periodic Background Tasks:

- Celery Beat periodically triggers data-fetch tasks without manual user intervention.
- This ensures data freshness and reduces the need for manual triggering.

## Testing

The project employs Pytest for unit and integration testing:

- Tests verify FastAPI endpoint functionality and database interactions.
- Background tasks are tested using mocks to avoid dependency on RabbitMQ during testing.

## Deployment

The architecture is Dockerized, making deployment straightforward in diverse environments.

- **Docker Compose** manages services including FastAPI, RabbitMQ, Celery Worker, and Celery Beat.
- Easy scaling and isolated environments simplify continuous integration and deployment.

## Scalability and Flexibility

- The use of Celery and RabbitMQ enables easy horizontal scaling of background tasks.
- SQLite can be easily replaced by more robust databases for production use.
- FastAPI supports asynchronous execution, maximizing API responsiveness.

## Conclusion

This architecture balances simplicity, efficiency, and scalability, providing a solid foundation for real-world backend applications.

