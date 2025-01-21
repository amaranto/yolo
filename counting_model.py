import asyncio, torch
from lib.tools.streamer import stream
from lib.models.counting import VisionTracking
from lib.models.pubsub import PostProcessing
from config import RTSP, logging, PUBSUB_TOPIC,PROJECT,POD,CHANNEL,SPOT, TRACK_CONF, TRACK_IOU, DEVICE

logger = logging.getLogger(__name__)

    
if torch.cuda.is_available():
    logger.info("CUDA is available")
    device = DEVICE if DEVICE else "0"
else:
    device = DEVICE if DEVICE else "cpu"
    logger.warning("CUDA NOT AVAILABLE !")     
        
async def main():

    pubsub = PostProcessing(
        topic = PUBSUB_TOPIC,
        project= PROJECT,
        pod = POD,
        channel= CHANNEL,
        spot = SPOT
    )

    countingVisionModelTracker = VisionTracking(
        model="./yolo/yolo11x.pt",
        post_processing_foo=pubsub.post_processing if PUBSUB_TOPIC else None,
        iou=TRACK_IOU,
        conf=TRACK_CONF,
        fps=5.0        
    )
    
    results = await asyncio.gather(
        stream(RTSP,  predict=[countingVisionModelTracker.predict],device=device),            
        countingVisionModelTracker.start(), 
    )
    
    print("Main function is done")
    print(results)

asyncio.run(main())