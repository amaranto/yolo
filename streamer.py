import asyncio
from lib.stream.streamer import streamer
from config import RTSP, INFERENCER_SERVER_ADRRESS, INFERENCER_PORT, STREAMER_OUTPUT_IMG, logging

logger = logging.getLogger(__name__)

while True:
    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(streamer(RTSP, inferencer_address=INFERENCER_SERVER_ADRRESS, port=INFERENCER_PORT, preview_img_output_file=STREAMER_OUTPUT_IMG)),
    ]
    
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
