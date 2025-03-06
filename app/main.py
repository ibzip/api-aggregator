from fastapi import FastAPI
from app.database import Base, engine
from app.routers import fetch, data

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_application() -> FastAPI:
    application = FastAPI(
        title="Aggregator Challenge",
        version="1.0.0"
    )
    application.include_router(fetch.router)
    application.include_router(data.router)
    return application

app = get_application()

# Create tables on startup
@app.on_event("startup")
def on_startup():
    create_tables()
