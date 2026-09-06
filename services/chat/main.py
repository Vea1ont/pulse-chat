import os

import sentry_sdk
from fastapi import FastAPI
from lifespan import lifespan
from prometheus_fastapi_instrumentator import Instrumentator
from routers import benchmark, chats

sentry_sdk.init(
    dsn=os.getenv("GLITCHTIP_DSN"),
    traces_sample_rate=0.01,  # 1% of transactions — adjust to your needs
    auto_session_tracking=False,  # GlitchTip does not support sessions
    # enable_logs=True,  # Opt-in: send logs to GlitchTip (uses disk space)
)

app = FastAPI(title="chat-service", lifespan=lifespan)

Instrumentator().instrument(app).expose(app)

app.include_router(chats.router, prefix="/api/v1")
app.include_router(benchmark.router)


@app.get("/health")
async def health():
    return {"service": "chat", "status": "ok"}
