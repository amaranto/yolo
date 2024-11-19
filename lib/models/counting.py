import cv2
import numpy as np
import asyncio 
import traceback
from time import sleep
from datetime import datetime
import numpy as np
from ultralytics import YOLO
from lib.tools.yolo import from_yolo_to_p1p2
from lib.tools.draw import draw_bboxes
from config import logging

logger=logging.getLogger(__name__)

class VisionTracking():
    def __init__(
        self,
        rtsp: str|None,
        model: str = "yolo11x.pt",
        preview_img: str = "output/counting-preview.jpg",
        fps: float = 20.0,
        fourcc: any = cv2.VideoWriter_fourcc('F', 'M', 'P', '4'),
        status_filter_foo:any=None,
        print_bbox:bool=True,
        loop_condition:any = lambda x : True,
        output_folder="output",
        classes: list[int] = [
            0, # person
            1, # bycycle
            2, # car
            3, # motorcycle
            5, # bus
            7, # truck
        ]        
    ):
        self.rtsp = rtsp
        self.model:any = YOLO(model)
        self.fps:float = fps
        self.status_filter_foo:any = status_filter_foo
        self.print_bbox:bool = print_bbox
        self.loop_condition:any = loop_condition
        self.classes:list[int] = classes
        self.preview_img:str = preview_img
        self.start_time: datetime = datetime.now()
        self.previous_frame: datetime = datetime.now()
        self.last_frame: datetime = datetime.now()
        self.output_folder = output_folder
        self.status = {
            "classes":{},
            "ids":{}
        }        
        self.fourcc = fourcc
        self.__video_output__ = None

    def __status_filter__(self, annotations:dict):
        frame_time = datetime.now()
        for annotation in annotations:
            track_id = annotation['track_id']
            class_name = 'motorcycle' if annotation['class_name'] == "bicycle" else annotation['class_name']

            if track_id not in self.status["ids"]:
                if class_name not in self.status["classes"]:
                    self.status["classes"][class_name] = { "total": 1 }  
                else: 
                    self.status["classes"][class_name]["total"] += 1
                self.status["classes"][class_name]["last_frame_time"] = frame_time

            self.status["ids"][track_id] = class_name
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
            "truck": (255,0,255),
            "car": (200,0,100),
            "motorcycle": (0,0,255),
            "person":(0,255,0),
            "cono": (100,100,100),
            "valde": (30,30,30),
            "extintor": (90,80,90),
            "default": (255,255,255)
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
            
        image = draw_bboxes(
            image, 
            [ 
                {
                    "text": f"{k} {v['total']}",
                    "color": class_colors[k] if k in class_colors else class_colors["default"]
                }
                for k,v in self.status["classes"].items() 
            ], 
            (0,0), 
            font_scale=0.5
        )
        
        return image
        
    def __enable_video_output__( self ):
        
        delta = self.last_frame - self.start_time
        return delta.seconds < 30 # Create a new stream after 1 hour   

    async def predict(self, img, tracker="bytetrack.yaml", conf=0.6, iou=0.3, persist=True):
        
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
        return img, results, annot
    
    async def stream(self):

        if self.rtsp is None:
            raise Exception("RTSP endpoint not configured !")
        
        cap = cv2.VideoCapture(self.rtsp)
        fps = cap.get(cv2.CAP_PROP_FPS)
        if cap.isOpened():
            ret, img= cap.read()
            logger.debug(f"Reading from rtsp at {fps} FPS")
            xSize, ySize, fps = int( cap.get(cv2.CAP_PROP_FRAME_WIDTH) ), int( cap.get(cv2.CAP_PROP_FRAME_HEIGHT) ), 90
            logger.info(f"RTSP connected Size: f{self.rtsp} | ({xSize}, {ySize}) | FPS:{fps}")
        else:
            raise Exception(f"Can not connecto to the stream {self.rtsp}")
        
        ret, img= cap.read()
        cv2.imwrite(self.preview_img, img)

        while cap.isOpened() and self.loop_condition(self.__dict__()):
            try:
                ret, img= cap.read()
                predict_task = asyncio.create_task( self.predict(img=img) )
                _, results, annotations = await predict_task
                self.status = self.status_filter_foo(annotations) if self.status_filter_foo else self.__status_filter__(annotations)

                img = self.__draw_bbox__( img, annotations ) if self.print_bbox else img 

                self.previous_frame = self.last_frame
                self.last_frame = datetime.now()

                if self.__enable_video_output__(): 
                
                    if self.__video_output__ is None:
                        xsize, ysize, _ = img.shape
                        timestmp = datetime.now().strftime('%Y-%m-%d_T%H:%M:%S.%f')
                        output_file = f"{self.output_folder}/counting-{timestmp}.avi"
                        self.__video_output__ = cv2.VideoWriter(output_file, self.fourcc, self.fps, (ysize, xsize) )      
                        logger.debug(f"Ready to write video to {output_file}. Frame: {xsize} {ysize}")
                
                    self.__video_output__.write(img)
                else:
                    self.__video_output__ = None

            except Exception as e:
                logger.error(str(e))
                traceback.print_exc()

        cap.release()
        logger.info("Model releasead !")     
       