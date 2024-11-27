import asyncio, torch
from lib.tools.streamer import stream
from lib.models.raizen import VisionTracking
from lib.models.pubsub import PostProcessing
from config import RTSP, logging, PUBSUB_TOPIC,PROJECT,POD,CHANNEL,SPOT, TRACK_CONF, TRACK_IOU

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    
    if torch.cuda.is_available():
        logger.info("CUDA is available")
    else:
        logger.warning("CUDA NOT AVAILABLE !")    

    pubsub = PostProcessing(
        topic = PUBSUB_TOPIC,
        project= PROJECT,
        pod = POD,
        channel= CHANNEL,
        spot = SPOT
    )

    cexpertVisionModelTracker = VisionTracking(
        model="./yolo/experto.pt",
        post_processing_foo=pubsub.post_processing if PUBSUB_TOPIC else None,
        iou=TRACK_IOU,
        conf=TRACK_CONF        
    )

    loop = asyncio.get_event_loop()

    while True:
        tasks = [
            loop.create_task(stream(RTSP,  models=[cexpertVisionModelTracker])),
        ]
        loop.run_until_complete(asyncio.wait(tasks))
        logger.debug("Stopping recording and detection for charge model")
