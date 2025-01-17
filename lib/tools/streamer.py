import cv2
import traceback
import asyncio
from config import logging

logger = logging.getLogger(__name__)

def stream(rtsp:str, predict:list[any], device="cpu"):

    if rtsp is None:
        raise Exception("RTSP endpoint not configured !")
    
    cap = cv2.VideoCapture(rtsp)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if cap.isOpened():
        ret, img= cap.read()
        logger.debug(f"Reading from rtsp at {fps} FPS")
        xSize, ySize, fps = int( cap.get(cv2.CAP_PROP_FRAME_WIDTH) ), int( cap.get(cv2.CAP_PROP_FRAME_HEIGHT) ), 90
        logger.info(f"RTSP connected Size: f{rtsp} | ({xSize}, {ySize}) | FPS:{fps}")
    else:
        raise Exception(f"Can not connecto to the stream {rtsp}")
    
    ret, img= cap.read()
    cv2.imwrite("output/preview-charge.jpg", img)

    while cap.isOpened():
        try:
            ret, img= cap.read()
            
            if img is None:
                logger.error("Can not read frame from stream. Releasing stream !")
                break
            
            for p in predict:
                p(img=img, device=device)
            
        except Exception as e:
            logger.error(str(e))
            traceback.print_exc()

    cap.release()
    logger.info("Camera releasead !")    
