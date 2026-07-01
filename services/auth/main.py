import os
import sentry_sdk

from fastapi import FastAPI, Depends, HTTPException


from prometheus_fastapi_instrumentator import Instrumentator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lifespan import lifespan

from routers import  auth, users

sentry_sdk.init(
    dsn=os.getenv("GLITCHTIP_DSN"),
    traces_sample_rate=0.01,  # 1% of transactions — adjust to your needs
    auto_session_tracking=False,  # GlitchTip does not support sessions
    # enable_logs=True,  # Opt-in: send logs to GlitchTip (uses disk space)
)

app = FastAPI(title="auth-service", lifespan=lifespan)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
Instrumentator().instrument(app).expose(app)

@app.get("/health")
async def health():
    return {"service": "auth", "status": "ok"}


