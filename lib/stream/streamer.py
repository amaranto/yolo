import socket, cv2
import numpy as np
import asyncio 
from time import sleep
from lib.yolo.detector import predict

from config import RTSP, logging

logger = logging.getLogger(__name__)

tcp = socket.SOCK_STREAM
afm = socket.AF_INET

async def write_img(img, path):
    cv2.imwrite(path, img)

async def streamer( rtsp:str , preview_img_output_file="output/stream.jpg", max_retries: int = 5, inferencer_address:str="127.0.0.1", port:int=2706):

    cap = cv2.VideoCapture(rtsp)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if cap.isOpened():
        ret, img= cap.read()
        logger.debug(f"Reading from rtsp at {fps} FPS")
        xSize, ySize, fps = int( cap.get(cv2.CAP_PROP_FRAME_WIDTH) ), int( cap.get(cv2.CAP_PROP_FRAME_HEIGHT) ), 120
        logger.info(f"RTSP connected Size: f{rtsp} | ({xSize}, {ySize}) | FPS:{fps}")
    else:
        raise Exception(f"Can not connecto to the stream {rtsp}")

    tries = 0
    while tries < max_retries:
        try:
            sb = socket.socket(afm,tcp)
            sb.connect((inferencer_address,port))
            break 
        except Exception as e:
            logger.error(f"Error connecting to vision socket. Try: {tries} Error: {e}")
            tries += 1
            sleep(0.5)

    if tries == max_retries:
        raise Exception("Can not connect to vision model socket")
    
    while cap.isOpened():
        ret, img= cap.read()

        _, img_encoded = cv2.imencode('.jpg', img)
        if preview_img_output_file:
            write_img_task = asyncio.create_task( write_img(img, preview_img_output_file) )

        img_encoded = img_encoded.tobytes()
        sb.sendall(img_encoded)

        if preview_img_output_file:
            await write_img_task

    cap.release()
    raise Exception("Connection to the streaming lost !")