import asyncio, torch
from lib.models.vision import VisionTracking
from lib.tools.draw import draw_tracking_charge_model
from config import INFERENCER_BIND_ADDRESS, INFERENCER_PORT, INFERENCER_OUTPUT_FILE, INFERENCER_FPS,logging

logger = logging.getLogger(__name__)

if torch.cuda.is_available():
    logger.info("CUDA is available")
else:
    logger.warning("CUDA NOT AVAILABLE !")
    
while True:
    visionTracker = VisionTracking(
        model="./yolo/yolo11x.pt",
        bind_address=INFERENCER_BIND_ADDRESS,
        fps=INFERENCER_FPS,
        port = INFERENCER_PORT,
        video_output=INFERENCER_OUTPUT_FILE,
        draw_foo=draw_tracking_charge_model
    )

    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(visionTracker.start()),
    ]

    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
