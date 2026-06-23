from fastapi import FastAPI

app = FastAPI(title="notify-service")


@app.get("/health")
async def health():
    return {"service": "notify", "status": "ok"}
