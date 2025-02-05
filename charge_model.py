import asyncio, torch
from sqlalchemy.sql import text
from lib.tools.streamer import stream
from lib.tools.yolo import from_p1p2_to_yolo
from lib.models.counting import ChargeTracking
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

chargeVisionModelTracker = ChargeTracking(
    model="./yolo/yolo11x.pt",
    model_type="carga",
    model_name=f"{SPOT}_{CHANNEL}",
    post_processing_foo=pubsub.post_processing if PUBSUB_TOPIC else None,
    iou=TRACK_IOU,
    conf=TRACK_CONF,
    fps=5.0,
    enable_video_output=True,
    classes= [
        0, # person
        1, # bycycle
        2, # car
        3, # motorcycle
        5, # bus
        7, # truck
        81, # Experto
        82, # Matafuego
        83, # Manguera
        84, # Balde
        85, # Cono
        86, # Valla
        87, # BocaCarga
        88, # Operario
        89  # CamionShell
    ]  
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
            chargeVisionModelTracker.roi = roi_yolo
        conn.close()            
        await asyncio.sleep(10)

            
async def main():    
    results = await asyncio.gather(
        get_roi(),
        stream(RTSP,  predict=[chargeVisionModelTracker.predict],device=device),            
        chargeVisionModelTracker.start(), 
    )
    
    print("Main function is done")
    print(results)

asyncio.run(main())