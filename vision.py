import os
from fastapi import FastAPI, APIRouter
from uvicorn import Server, Config
from starlette.middleware.cors import CORSMiddleware

from routes.predict import router as prediction_router

router = APIRouter(tags=["Image Upload and analysis"], prefix="/yolo")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prediction_router)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    server = Server(Config(app, host="0.0.0.0", port=port, lifespan="on"))
    server.run()