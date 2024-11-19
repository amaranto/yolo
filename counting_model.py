import asyncio, torch
from datetime import datetime
from lib.models.counting import VisionTracking
from config import RTSP,logging

logger = logging.getLogger(__name__)

if torch.cuda.is_available():
    logger.info("CUDA is available")
else:
    logger.warning("CUDA NOT AVAILABLE !")

# def break_loop_after_1h( status: dict ):
#     delta = status["last_frame"] - status["start_time"]
#     return delta.seconds < 3600 # Create a new stream after 1 hour

loop = asyncio.get_event_loop()

while True:
    timestmp = datetime.now().strftime('%Y-%m-%d_T%H:%M:%S.%f')
    visionTracker = VisionTracking(
        model="./yolo/yolo11x.pt",
        rtsp=RTSP,
    )

    tasks = [
        loop.create_task(visionTracker.stream()),
    ]

    loop.run_until_complete(asyncio.wait(tasks))
    del visionTracker