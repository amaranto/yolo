import os
import requests
from fastapi import FastAPI, Request
from uvicorn import Server, Config
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from routes.yolo import router as prediction_router
from routes.streaming import router as streaming_router
from routes.health import router as health_checks
from config import CORS_ORIGIN, AUTH_ENDPOINT, ENABLE_AUTH, logging

logger = logging.getLogger(__name__)

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

def check_permission(method, api, auth):

    if method == 'GET' and api[1:] in ['healthz', '/'] or api[1:] == "":
        return True
    
    scheme, data = (auth or ' ').split(' ', 1)
    if scheme != 'Bearer': 
        return False
    
    r=requests.get(AUTH_ENDPOINT, headers={
        "Authorization": auth
    })
    if r.status_code == 200:
        return True
    else:
        logger.info(f"User unauthorized {r.status_code}")
        return False

@app.middleware("http")
async def check_authentication(request: Request, call_next):
    auth = request.headers.get('Authorization') 

    if request.method == "OPTIONS":
        return JSONResponse(None, status_code=200)

    if not check_permission(request.method, request.url.path, auth) and ENABLE_AUTH:
        return JSONResponse(None, 401, {"WWW-Authenticate": "Basic"})
    return await call_next(request)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    server = Server(Config(app, host="0.0.0.0", port=port, lifespan="on"))
    server.run()