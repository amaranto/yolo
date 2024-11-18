import asyncio, torch
from datetime import datetime
from lib.models.vision import VisionTracking
from lib.tools.draw import draw_tracking_charge_model
from config import INFERENCER_BIND_ADDRESS, INFERENCER_PORT, INFERENCER_OUTPUT_FILE, INFERENCER_FPS,logging

logger = logging.getLogger(__name__)

if torch.cuda.is_available():
    logger.info("CUDA is available")
else:
    logger.warning("CUDA NOT AVAILABLE !")

def break_loop_if_truck (status: dict):
    return not "truck" in status["status"]["classes"]

def break_loop_if_not_track( status: dict ):

    truck_is_present = "truck" in status["status"]["classes"]
    if truck_is_present:
        last_truck_frame_delta = datetime.now() - status["status"]["classes"]["truck"]["last_frame_time"]
        return last_truck_frame_delta.seconds < 60
    
    start_time_delta = datetime.now() - status["start_time"]
    return start_time_delta.seconds < 60

loop = asyncio.get_event_loop()

while True:

    visionTrackerWithoutRecording = VisionTracking(
        model="./yolo/yolo11x.pt",
        bind_address=INFERENCER_BIND_ADDRESS,
        fps=INFERENCER_FPS,
        port = INFERENCER_PORT,
        video_output=None,
        draw_foo=draw_tracking_charge_model,
        loop_condition=break_loop_if_truck
    )

    tasks = [
        loop.create_task(visionTrackerWithoutRecording.start()),
    ]
    loop.run_until_complete(asyncio.wait(tasks))
    del visionTrackerWithoutRecording 

    timestmp = datetime.now().strftime('%Y-%m-%d_T%H:%M:%S.%f')
    visionTrackerRecording = VisionTracking(
        model="./yolo/yolo11x.pt",
        bind_address=INFERENCER_BIND_ADDRESS,
        fps=INFERENCER_FPS,
        port = INFERENCER_PORT,
        video_output=f"output/charge-{timestmp}.avi",
        draw_foo=draw_tracking_charge_model,
        loop_condition=break_loop_if_not_track
    )

    tasks = [
        loop.create_task(visionTrackerRecording.start()),
    ]

    loop.run_until_complete(asyncio.wait(tasks))

    del visionTrackerRecording
    logger.debug("Stopping recording and detection for charge model")