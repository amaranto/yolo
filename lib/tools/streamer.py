import cv2
import traceback
import asyncio
from datetime import datetime
from config import logging

logger = logging.getLogger(__name__)

async def stream(rtsp:str, predict:list[any], device="cpu"):
    if rtsp is None:
        raise Exception("RTSP endpoint not configured !")
    
    while True:
        logger.info("Starting rtsp connection ... ")
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

        frame_count = 0
        frame_time = datetime.now()
        
        while cap.isOpened():
            try:
                # Limit the frame rate to 10 FPS
                if frame_count > 10 or (datetime.now() - frame_time).total_seconds() > 1:
                    frame_count = 0
                    frame_time = datetime.now()
                    continue
                
                c1 = cv2.getTickCount()
                ret, img= cap.read()
                
                if img is None:
                    logger.error("Can not read frame from stream. Releasing stream !")
                    break
                
                for p in predict:
                    await p(img=img, device=device)
                                    
                c2 = cv2.getTickCount()
                time_taken = (c2 - c1)/ cv2.getTickFrequency() 
                await asyncio.sleep(0.001)
                logger.info(f"Stream rate: {round(1/time_taken)}")
                
            except Exception as e:
                logger.error(str(e))
                traceback.print_exc()

        cap.release()
        logger.info("Camera releasead !")    
