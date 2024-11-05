import asyncio
from lib.stream.streamer import receive, rtsp
from config import RTSP, logging

logger = logging.getLogger(__name__)

while True:
    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(receive()),
    ]

    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
