from fastapi import FastAPI

app = FastAPI(
    title="Portfolio Agent API",
    version="1.0.0",
    description="Personal Wealth Management Backend"
)


@app.get("/")
def root():
    return {
        "message": "Portfolio Agent API is running 🚀"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }