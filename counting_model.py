import asyncio, torch
from sqlalchemy.sql import text
from lib.tools.streamer import stream
from lib.tools.yolo import from_p1p2_to_yolo
from lib.models.counting import VisionTracking
from lib.models.pubsub import PostProcessing
from lib.gcp.cloudsql import pool
from config import RTSP, logging, PUBSUB_TOPIC,PROJECT, POD,CHANNEL,SPOT, TRACK_CONF, TRACK_IOU, DEVICE

logger = logging.getLogger(__name__)

    
if torch.cuda.is_available():
    logger.info("CUDA is available")
    device = DEVICE if DEVICE else "0"
else:
    device = DEVICE if DEVICE else "cpu"
    logger.warning("CUDA NOT AVAILABLE !")     
        
pubsub = PostProcessing(
    topic = PUBSUB_TOPIC,
    project= PROJECT,
    pod = POD,
    channel= CHANNEL,
    spot = SPOT
)

countingVisionModelTracker = VisionTracking(
    model="./yolo/yolo11x.pt",
    model_name=f"{SPOT}_{CHANNEL}",
    model_type="conteo",
    post_processing_foo=pubsub.post_processing if PUBSUB_TOPIC else None,
    iou=TRACK_IOU,
    conf=TRACK_CONF,
    fps=5.0        
)


async def get_roi():
    query = text(
        "SELECT x1,x2,y1,y2,width,height FROM Segmentations WHERE station=':station' AND channel=':channel'"
    )
    while True:
        conn = pool.connect()
        result = conn.execute(query, { "station": SPOT, "channel": CHANNEL }).fetchone()
        logger.info(f"ROI: {result}")
        
        if result:
            x1,x2,y1,y2,w,h = result
            x1,x2,y1,y2,w,h = int(float(x1)), int(float(x2)), int(float(y1)), int(float(y2)), int(float(w)), int(float(h))
            roi_yolo = from_p1p2_to_yolo((x1,y1), (x2,y2), (h,w))
            countingVisionModelTracker.roi = roi_yolo
        conn.close()            
        await asyncio.sleep(10)

            
async def main():    
    results = await asyncio.gather(
        get_roi(),
        stream(RTSP,  predict=[countingVisionModelTracker.predict],device=device),            
        countingVisionModelTracker.start(), 
    )
    
    print("Main function is done")
    print(results)

asyncio.run(main())