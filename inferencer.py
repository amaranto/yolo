import asyncio, torch
from lib.stream.streamer import inferencer
from config import INFERENCER_BIND_ADDRESS, INFERENCER_PORT, INFERENCER_OUTPUT_FILE, INFERENCER_FPS,logging

logger = logging.getLogger(__name__)

if torch.cuda.is_available():
    logger.info("CUDA is available")
else:
    logger.warning("CUDA NOT AVAILABLE !")
    
while True:
    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(inferencer(
            address=INFERENCER_BIND_ADDRESS,
            port=INFERENCER_PORT,
            video_path=INFERENCER_OUTPUT_FILE,
            fps=INFERENCER_FPS
            )),
    ]

    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
