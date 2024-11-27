import cv2
import numpy as np
import asyncio
import traceback
import numpy as np
from asyncio import AbstractEventLoop
from typing import Callable
from datetime import datetime
from ultralytics import YOLO
from lib.tools.yolo import from_yolo_to_p1p2
from lib.tools.draw import draw_bboxes
from config import logging

logger=logging.getLogger(__name__)

class VisionTracking():
    def __init__(
        self,
        model: str,
        fps: float = 10.0,
        model_type: str = "carga",
        conf:float=0.6,
        iou:float=0.5,        
        fourcc: any = cv2.VideoWriter_fourcc(*'VP90'),
        status_filter_foo:Callable|None=None,
        post_processing_foo:Callable|None = None,
        print_bbox:bool=True,
        output_folder:str="output",
        classes: list[int] = [
            0, #Experto
            1, #Matafuego
            2, #Manguera
            3, #Balde
            4, #Cono
            5, #Valla
        ],
    ):
        self.model:any = YOLO(model)
        self.fps:float = fps
        self.print_bbox:bool = print_bbox
        self.model_type = model_type
        self.status_filter_foo:Callable = status_filter_foo
        self.post_processing_foo:Callable = post_processing_foo
        self.classes:list[int] = classes
        self.start_time: datetime = datetime.now()
        self.previous_frame: datetime = datetime.now()
        self.last_frame: datetime = datetime.now()
        self.output_folder = output_folder
        self.status = {
            "model": self.model_type,
            "classes":{},
            "ids":{}
        }        
        self.conf = conf
        self.iou = iou 
        self.fourcc = fourcc
        self.__video_output__ = None
        self.post_processing_tasks = []

    def __status_filter__(self, annotations:dict):

        frame_time = datetime.now()

        for annotation in annotations:
            track_id = annotation['track_id']
            class_name = annotation['class_name']

            if class_name not in self.status["classes"]:
                self.status["classes"][class_name] = { "total": 1 }                      
            self.status["classes"][class_name]["last_frame_time"] = frame_time
            
            if track_id not in self.status["ids"]:
                self.status["ids"][track_id] = class_name
                self.status["classes"][class_name]["total"] += 1

        return self.status 
    
    def __dict__(self):
        return {          
            "status": self.status,
            "start_time": self.start_time,
            "previous_frame": self.previous_frame,
            "last_frame": self.last_frame,
            "fps": self.fps,
            "classes": self.classes
        }

    def __draw_bbox__(self,image, annotations):
        
        class_colors = {
            "Experto": (255,0,255),
            "Matafuego": (200,0,100),
            "Manguera": (0,0,255),
            "Balde":(0,255,0),
            "Cono": (100,100,100),
            "Valla": (30,30,30),
            "default": (255,255,255)
        }

        output=None

        for annotation in annotations:
            p1,p2 = from_yolo_to_p1p2(
                annotation["x"],
                annotation["y"],
                annotation["w"],
                annotation["h"], 
                (image.shape[0], image.shape[1]) 
            )

            conf = annotation['conf']
            track_id = annotation['track_id']
            class_name = annotation['class_name']
            if class_name in class_colors:
                output = draw_bboxes(
                    image, 
                    [{ 
                        "text": f"{track_id}: {class_name} {conf}",
                        "color": class_colors[class_name] if class_name in class_colors else class_colors["default"]
                    }], 
                    p1,p2, 
                    font_scale=0.3
                )

        output = draw_bboxes(
            output if output is not None else image, 
            [ 
                {
                    "text": f"{cls}",
                    "color": (0,255,0) if cls in self.status["classes"] else (0,0,255)
                } 
                for cls,_ in class_colors.items() 
            ], 
            (0,0), 
            font_scale=0.5, 
        )

        return  output
        
    def __enable_video_output__( self ):
        
        delta = self.last_frame - self.start_time
        logger.debug(delta.seconds)
        return delta.seconds < 3600 
        
    def __post_predict_actions__(self, img, annotations):
        self.status = self.status_filter_foo(annotations) if self.status_filter_foo else self.__status_filter__(annotations)

        img = self.__draw_bbox__( img, annotations ) if self.print_bbox else img 

        self.previous_frame = self.last_frame

        if self.__enable_video_output__(): 
        
            if self.__video_output__ is None:
                xsize, ysize, _ = img.shape
                timestmp = datetime.now().strftime('%Y-%m-%d_T%H:%M:%S.%f')
                output_file = f"{self.output_folder}/experto-{timestmp}.webm"
                self.__video_output__ = cv2.VideoWriter(output_file, self.fourcc, self.fps, (ysize, xsize) )      
                logger.debug(f"Ready to write video to {output_file}. Frame: {xsize} {ysize}")

            logger.debug(f"Video output enabled.")
            self.__video_output__.write(img)
        else:
            self.start_time = datetime.now()
            self.__video_output__ = None

        self.last_frame = datetime.now()

    async def predict(self, img, tracker:str="bytetrack.yaml", conf:float|None=None, iou=None, persist:float|None=True):

        conf = conf if conf else self.conf
        iou = iou if iou else self.iou

        results = self.model.track(img, tracker=tracker, classes=self.classes, conf=conf, iou=iou, persist=persist)
        annot = []
        for result in results:
            boxes = result.boxes 

            if boxes.id is None: 
                continue

            for id, cls, (x,y,w,h), conf in zip(boxes.id, boxes.cls, boxes.xywhn, boxes.conf):

                id = int(id)
                clsId = int(cls)
                clsName = self.model.names[clsId]
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

        if self.post_processing_foo:
            self.post_processing_tasks.append( 
                asyncio.create_task(    
                    self.post_processing_foo(annot.copy(), self.status.copy())
                )
            )

        self.__post_predict_actions__(img, annot)

        if self.post_processing_foo:
            await asyncio.gather(*self.post_processing_tasks)

        return img, results, annot
