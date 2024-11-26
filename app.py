import os
from fastapi import FastAPI, APIRouter
from uvicorn import Server, Config
from fastapi.middleware.cors import CORSMiddleware

from routes.yolo import router as prediction_router
from routes.streaming import router as streaming_router
from routes.health import router as health_checks
from config import CORS_ORIGIN
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGIN,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prediction_router)
app.include_router(streaming_router)
app.include_router(health_checks)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    server = Server(Config(app, host="0.0.0.0", port=port, lifespan="on"))
    server.run()