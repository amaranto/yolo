import asyncio, torch
from datetime import datetime
from lib.models.charge import VisionTracking
from config import RTSP, logging

logger = logging.getLogger(__name__)

if torch.cuda.is_available():
    logger.info("CUDA is available")
else:
    logger.warning("CUDA NOT AVAILABLE !")

loop = asyncio.get_event_loop()

while True:
    timestmp = datetime.now().strftime('%Y-%m-%d_T%H:%M:%S.%f')

    visionTrackerWithoutRecording = VisionTracking(
        model="./yolo/yolo11x.pt",
        rtsp=RTSP,
    )

    tasks = [
        loop.create_task(visionTrackerWithoutRecording.stream()),
    ]
    loop.run_until_complete(asyncio.wait(tasks))
    del visionTrackerWithoutRecording 

    logger.debug("Stopping recording and detection for charge model")