import numpy as np
from ultralytics import YOLO

from lib.tools.yolo import from_yolo_to_p1p2
from config import logging
logger=logging.getLogger(__name__)
model = YOLO("./yolo/yolo11x.pt")
classes = [
    0, # person
    1, # bycycle
    2, # car
    3, # motorcycle
    5, # bus
    7, # truck
]

async def predict(img):
    
    results = model.track(img, tracker="bytetrack.yaml", classes=classes, conf=0.4, iou=0.5, persist=True)
    annot = []
    for result in results:
        boxes = result.boxes 
        for id, cls, (x,y,w,h), conf in zip(boxes.id, boxes.cls, boxes.xywhn, boxes.conf):

            id = int(id)
            clsId = int(cls)
            clsName = model.names[clsId]
            conf = np.round( conf * 100 )

            annot.append(
                {
                    "x":x,
                    "y":y,
                    "w":w,
                    "h":h,
                    "track_id": id,
                    "class_id": clsId,
                    "class_name": clsName,
                    "conf": conf
                }
            )
    return img, results, annot