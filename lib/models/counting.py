import cv2
import numpy as np
import asyncio 
import numpy as np
from datetime import datetime
from typing import Callable
from ultralytics import YOLO
from lib.tools.yolo import from_yolo_to_p1p2, from_p1p2_to_yolo
from lib.tools.draw import draw_bboxes
from config import logging

logger=logging.getLogger(__name__)

import cv2
import numpy as np
import asyncio
import numpy as np
from typing import Callable
from datetime import datetime
from ultralytics import YOLO
from lib.tools.yolo import from_yolo_to_p1p2
from lib.tools.draw import draw_bboxes
from config import logging

logger=logging.getLogger(__name__)


class BaseModel():
    def __init__(
        self,
        model: str,
        model_name: str,
        model_type: str = "carga",        
        fps: float = 10.0,
        conf:float=0.6,
        iou:float=0.5,        
        roi: tuple[int,int,int,int]|None = (0.5,0.5,1,1), # ROI in YOLO format
        fourcc: any = cv2.VideoWriter_fourcc(*'VP90'),
        status_filter_foo:Callable|None=None,
        post_processing_foo:Callable|None = None,
        print_bbox:bool=True,
        output_folder:str="output",
        classes: list[int] = [
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
        ],
        enable_video_output:bool=True
    ):
        self.model:any = YOLO(model)
        self.model_name = model_name
        self.model_type = model_type        
        self.fps:float = fps
        self.roi:tuple[int,int,int,int] = roi
        self.process_rate: float = 0.0
        self.print_bbox:bool = print_bbox
        self.status_filter_foo:Callable = status_filter_foo
        self.post_processing_foo:Callable = post_processing_foo
        self.classes:list[int] = classes
        self.start_frame: datetime = datetime.now()
        self.last_frame: datetime = datetime.now()
        self.output_folder = output_folder
        self.status = {
            "model": self.model_type,
            "classes":{},
            "ids":{}
        }        
        self.state:list[dict] = []
        self.is_alive: bool = True        
        self.conf = conf
        self.iou = iou 
        self.fourcc = fourcc
        self.__enable_video_output__: bool = enable_video_output
        self.__video_output__ = None
        self.__current_video_output__ = None

    def __status_filter__(self, annotations:dict):

        frame_time = datetime.now()

        for annotation in annotations:
            track_id = annotation['track_id']
            class_name = 'motorcycle' if annotation['class_name'] == "bicycle" else annotation['class_name']

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
            "start_frame": self.start_frame,
            "last_frame": self.last_frame,
            "fps": self.fps,
            "classes": self.classes
        }

    def __draw_bbox__(self,image, annotations, draw_roi=True):

        class_colors = {
            "truck": (255,0,255),
            "car": (200,0,100),
            "motorcycle": (0,0,255),
            "person":(0,255,0),
            "cono": (100,100,100),
            "valde": (30,30,30),
            "extintor": (90,80,90),
            "default": (255,255,255),
            "roi": (100,150,200)
        }

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
            class_name = 'motorcycle' if annotation['class_name'] == "bicycle" else annotation['class_name']
            text = f"{track_id}: {class_name} {conf}"
            color = class_colors[class_name] if class_name in class_colors else class_colors["default"]
            image = draw_bboxes(image, [{"text": text, "color": color}], p1,p2, font_scale=0.3)
        
        display = [
            {
                "text": f"FPS: {self.process_rate}",
                "color": (255,255,255)
            }   
        ]
        
        display += [ 
            {
                "text": f"{k} {v['total']}",
                "color": class_colors[k] if k in class_colors else class_colors["default"]
            }
            for k,v in self.status["classes"].items() 
        ]
                
        image = draw_bboxes(
            image, 
            display, 
            (0,0), 
            font_scale=0.5
        )
        
        if draw_roi:
            p1,p2 = from_yolo_to_p1p2(self.roi[0], self.roi[1], self.roi[2], self.roi[3], (image.shape[0], image.shape[1]) )
            image = draw_bboxes(
                image,
                [ 
                    {
                        "text": "",
                        "color": class_colors["roi"]
                    }
                ], 
                p1,
                p2,
                font_scale=0.0,
                thickness=5,
                lineType=2
            )
            
        return image

    def __generate_video_output__(self, xsize, ysize):
        if self.__video_output__:
            self.__video_output__.release()
            self.__video_output__ = None
 
        self.start_frame = datetime.now()
        timestmp = self.start_frame.strftime('%Y-%m-%d_T%H-%M-%S')
        output_file = f"{self.output_folder}/{self.model_type}-{self.model_name}-{timestmp}.webm"
        self.__current_video_output__ = output_file        
        self.__video_output__ = cv2.VideoWriter(output_file, self.fourcc, self.fps, (ysize, xsize) )      
        logger.debug(f"Ready to write video to {output_file}. Frame: {xsize} {ysize}")
        return self.__video_output__
    
    def __has_to_rotate_video__( self ):
        delta = self.last_frame - self.start_frame
        logger.debug(delta.seconds)
        return delta.seconds > 3600 or not self.__video_output__ # Create a new stream after 1 hour  
    
    def __post_predict_actions__(self, img, annotations):
        self.status = self.status_filter_foo(annotations) if self.status_filter_foo else self.__status_filter__(annotations)

        img = self.__draw_bbox__( img, annotations) if self.print_bbox else img 
        xsize, ysize, _ = img.shape
        
        if self.__has_to_rotate_video__(): 
            self.__generate_video_output__(xsize, ysize)
        logger.info(f"Video output enabled: {self.__enable_video_output__}")

        if self.__enable_video_output__:
            self.__video_output__.write(img)

    async def start(self):
        logger.info("Model started")

        while self.is_alive:
                
            if self.state:
                
                data = self.state.pop(0)
                current_img = data["img"]
                current_annot = data["annotations"]
                
                self.__post_predict_actions__(current_img, current_annot)
                if self.post_processing_foo and self.__enable_video_output__:
                    async_foo = asyncio.create_task(    
                        self.post_processing_foo(current_annot.copy(), self.status.copy())
                    )                    
                    await asyncio.gather(async_foo)  
                
                current_frame = datetime.now()
                self.process_rate = round(1/(current_frame - self.last_frame).total_seconds())
                self.last_frame = current_frame
                logger.info(f"Throughput FPS: {self.process_rate}")

            await asyncio.sleep(0.01)

    def stop(self):
        self.is_alive = False
        return True
    
    async def predict(self, img, tracker:str="bytetrack.yaml", conf:float|None=None, iou=None, persist:float|None=True, device="cpu"):
        
        conf = conf if conf else self.conf
        iou = iou if iou else self.iou
        rx, ry, rw, rh = self.roi
        results = self.model.track(img, tracker=tracker, classes=self.classes, conf=conf, iou=iou, persist=persist, device=device)
        # results = self.model.track(img, tracker=tracker,  conf=conf, iou=iou, persist=persist, device=device)
        annot = []
        for result in results:
            boxes = result.boxes 

            if boxes.id is None: 
                continue

            for id, cls, (x,y,w,h), conf in zip(boxes.id, boxes.cls, boxes.xywhn, boxes.conf):
                if not (rx-(rw/2) < x < rx+(rw/2) and ry-(rh/2) < y < ry+(rh/2)):
                    continue
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
                        "conf": conf,
                        "video_name": self.__current_video_output__,
                    }
                )
                
        self.state.append({
            "img": img,
            "annotations": annot.copy()
        })
        return img, results, annot
 
class VisionTracking(BaseModel):
    pass

class ChargeTracking(BaseModel):
    def __has_to_rotate_video__( self ):
        
        current_time = datetime.now() 
        truck_is_present = "truck" in self.status["classes"]
        if truck_is_present:
            last_truck_frame_delta = current_time - self.status["classes"]["truck"]["last_frame_time"]
            
            if last_truck_frame_delta.seconds < 60 and not self.__video_output__:
                logger.info("Truck is present. Creating new video output")
                self.__enable_video_output__ = True
                return True
            elif last_truck_frame_delta.seconds < 60 and self.__video_output__:
                self.__enable_video_output__ = True
                logger.info(f"Delta {last_truck_frame_delta.seconds} .Writting output to {self.__current_video_output__}")
                return False
            elif last_truck_frame_delta.seconds > 60:
                # Delete track from status if not truck is present after 60 seconds
                logger.info("Not Truck detected after 60 seconds. Disabling video output")
                self.__enable_video_output__ = False      
                # removing truck from status          
                self.status["classes"].pop('truck', None)
                return True
        elif not truck_is_present and not self.__video_output__:
            logger.info("Preparing new video output and waiting for truck to arrive")
            self.__enable_video_output__ = False
            return True
        else:
            logger.info("Truck is not present in current status.")
            return False