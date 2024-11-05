import os
import logging

RTSP_ENDPOINT=os.getenv("RTSP_ENDPOINT", "11.37.69.100/cam/realmonitor?channel=9&subtype=1")
RTSP_USER=os.getenv("RTSP_USER")
RTSP_PWD=os.getenv("RTSP_PWD")

RTSP=f"rtsp://{RTSP_USER}:{RTSP_PWD}@" if RTSP_USER and RTSP_PWD else "rtsp://"
RTSP=f"{RTSP}{RTSP_ENDPOINT}"
RTSP="rtsp://proyecto:proyecto2024@11.37.69.100/cam/realmonitor?channel=9&subtype=1"

logging.basicConfig(level=logging.DEBUG)
