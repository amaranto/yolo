import asyncio, torch
from datetime import datetime
from lib.models.counting import VisionTracking
from lib.models.pubsub import PostProcessing
from config import RTSP, logging, PUBSUB_TOPIC,PROJECT,POD,CHANNEL,SPOT

logger = logging.getLogger(__name__)

if torch.cuda.is_available():
    logger.info("CUDA is available")
else:
    logger.warning("CUDA NOT AVAILABLE !")

loop = asyncio.get_event_loop()

pubsub = PostProcessing(
    topic = PUBSUB_TOPIC,
    project= PROJECT,
    pod = POD,
    channel= CHANNEL,
    spot = SPOT
)

while True:
    timestmp = datetime.now().strftime('%Y-%m-%d_T%H:%M:%S.%f')
    visionTracker = VisionTracking(
        model="./yolo/yolo11x.pt",
        rtsp=RTSP,
        post_processing_foo=pubsub.post_processing if PUBSUB_TOPIC else None    
    )

    tasks = [
        loop.create_task(visionTracker.stream()),
    ]

    loop.run_until_complete(asyncio.wait(tasks))
    del visionTracker