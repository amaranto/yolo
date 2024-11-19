import os
import logging

RTSP_ENDPOINT=os.getenv("RTSP_ENDPOINT", "127.0.0.1/cam/realmonitor?channel=9&subtype=1")
RTSP_USER=os.getenv("RTSP_USER", None)
RTSP_PWD=os.getenv("RTSP_PWD", None)

RTSP=f"rtsp://{RTSP_USER}:{RTSP_PWD}@" if RTSP_USER and RTSP_PWD else "rtsp://"
RTSP=f"{RTSP}{RTSP_ENDPOINT}"
cors_origin=os.getenv("CORS_ORIGIN", None)
CORS_ORIGIN=cors_origin.split(",") if cors_origin else ["*"]
logging.basicConfig(level=logging.DEBUG)

if not os.path.isdir('output'):
    os.mkdir("output")