from fastapi import FastAPI
from sqlalchemy import text

from app.api.auth import router as auth_router
from app.database.session import engine

app = FastAPI(
    title="Portfolio Agent API",
    version="1.0.0",
)

app.include_router(auth_router)


@app.get("/")
def root():
    return {"message": "Portfolio Agent API is running 🚀"}


@app.get("/health")
def health():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "status": "healthy",
        "database": "connected",
    }