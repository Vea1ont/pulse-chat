import os
import sentry_sdk

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

sentry_sdk.init(
    dsn=os.getenv("GLITCHTIP_DSN"),
    traces_sample_rate=0.01,  # 1% of transactions — adjust to your needs
    auto_session_tracking=False,  # GlitchTip does not support sessions
    # enable_logs=True,  # Opt-in: send logs to GlitchTip (uses disk space)
)


app = FastAPI(title="notify-service")

Instrumentator().instrument(app).expose(app)

@app.get("/health")
async def health():
    return {"service": "notify", "status": "ok"}
