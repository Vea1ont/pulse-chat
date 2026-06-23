from fastapi import FastAPI

app = FastAPI(title="auth-service")


@app.get("/health")
async def health():
    return {"service": "auth", "status": "ok"}
