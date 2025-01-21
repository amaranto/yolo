import os
import logging

RTSP_ENDPOINT=os.getenv("RTSP_ENDPOINT", "127.0.0.1/cam/realmonitor?channel=9&subtype=1")
RTSP_USER=os.getenv("RTSP_USER", None)
RTSP_PWD=os.getenv("RTSP_PWD", None)

RTSP=f"rtsp://{RTSP_USER}:{RTSP_PWD}@" if RTSP_USER and RTSP_PWD else "rtsp://"
RTSP=f"{RTSP}{RTSP_ENDPOINT}"
cors_origin=os.getenv("CORS_ORIGIN", None)
CORS_ORIGIN=cors_origin.split(",") if cors_origin else ["*"]

POD = os.getenv("POD", "undefined")
PUBSUB_TOPIC = os.getenv("PUBSUB_TOPIC", None)
PROJECT = os.getenv("GCP_PROJECT", None)
SPOT = int( os.getenv("SPOT", "-1") )
CHANNEL = int( os.getenv("CHANNEL", "-1"))
MODEL_TYPE= os.getenv("MODEL_TYPE", "undifined")

TRACK_CONF=float(os.getenv("TRACK_CONF", "0.1"))
TRACK_IOU=float(os.getenv("TRACK_IOU", "0.9"))

AUTH_ENDPOINT=os.getenv("AUTH_ENDPOINT", "https://raizen-sm-cloudrun-980463466363.us-central1.run.app/api/auth/check")
ENABLE_AUTH=True if os.getenv("ENABLE_AUTH", "true").lower() == "true" else False

DEVICE=os.getenv("DEVICE", None)

degub_levels = {
    "CRITICAL": 50,
    "ERROR": 40,
    "WARNING": 30,
    "INFO": 20,
    "DEBUG": 10,
    "NOTSET": 0
}


DEBUG=os.getenv("DEBUG", "INFO").upper()
DEBUG=logging.INFO if DEBUG not in degub_levels else degub_levels[DEBUG]
logging.basicConfig(level=DEBUG)

if not os.path.isdir('output'):
    os.mkdir("output")