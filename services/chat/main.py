from fastapi import FastAPI

app = FastAPI(title="chat-service")


@app.get("/health")
async def health():
    return {"service": "chat", "status": "ok"}
