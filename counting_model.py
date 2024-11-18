import asyncio, torch
from datetime import datetime
from lib.models.vision import VisionTracking
from lib.tools.draw import draw_tracking_counting_model
from config import INFERENCER_BIND_ADDRESS, INFERENCER_PORT, INFERENCER_OUTPUT_FILE, INFERENCER_FPS,logging

logger = logging.getLogger(__name__)

if torch.cuda.is_available():
    logger.info("CUDA is available")
else:
    logger.warning("CUDA NOT AVAILABLE !")

def break_loop_after_1h( status: dict ):
    delta = status["last_frame"] - status["start_time"]
    return delta.seconds < 3600 # Create a new stream after 1 hour

loop = asyncio.get_event_loop()

while True:
    timestmp = datetime.now().strftime('%Y-%m-%d_T%H:%M:%S.%f')
    visionTracker = VisionTracking(
        model="./yolo/yolo11x.pt",
        bind_address=INFERENCER_BIND_ADDRESS,
        fps=INFERENCER_FPS,
        port = INFERENCER_PORT,
        video_output=f"output/counting-{timestmp}.avi",
        draw_foo=draw_tracking_counting_model,
        loop_condition=break_loop_after_1h
    )

    tasks = [
        loop.create_task(visionTracker.start()),
    ]

    loop.run_until_complete(asyncio.wait(tasks))
    del visionTracker