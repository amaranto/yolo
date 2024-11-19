import socket, cv2
import numpy as np
import asyncio 
import traceback
from time import sleep
from datetime import datetime
import numpy as np
from ultralytics import YOLO
from config import logging

logger=logging.getLogger(__name__)

class VisionTracking():
    def __init__(
        self,
        model: str = "yolo11x.pt",
        bind_address: str = "127.0.0.1",
        port: int = 2706,
        buffer: int = 1921600,
        video_output: str|None = "output/output.avi",
        fps: float = 90.0,
        fourcc: any = cv2.VideoWriter_fourcc('F', 'M', 'P', '4'),
        status_filter_foo:any= None,
        draw_foo:any=None,
        loop_condition:any = lambda x : True,
        classes: list[int] = [
            0, # person
            1, # bycycle
            2, # car
            3, # motorcycle
            5, # bus
            7, # truck
        ]        
    ):
        self.model:any = YOLO(model)
        self.bind_address:str = bind_address
        self.port:int = port
        self.buffer:int = buffer
        self.fps:float = fps
        self.status_filter_foo:any = status_filter_foo
        self.draw_foo:any = draw_foo
        self.loop_condition:any = loop_condition
        self.tcp = socket.SOCK_STREAM
        self.afm = socket.AF_INET
        self.classes:list[int] = classes
        self.video_output:str = video_output
        self.start_time: datetime = datetime.now()
        self.previous_frame: datetime = datetime.now()
        self.last_frame: datetime = datetime.now()
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
    
    async def start(self):

        sa = socket.socket(self.afm, self.tcp)
        sa.bind((self.bind_address, self.port))
        sa.listen()
        logger.debug("Waiting for connections ...")
        session, _ = sa.accept()
        logger.debug("New incomming connection ...")
        
        image = None
        while self.video_output:
            logger.debug(f"Starting protocol from buffer to avi.")
            img_encoded = session.recv(self.buffer)
            image_arr = np.frombuffer(img_encoded,np.uint8)
            image = cv2.imdecode(image_arr, cv2.IMREAD_COLOR)
            if image is None:
                logger.error(f"Video output enabled but error triggered reading initial buffer.")
                sleep(0.5)
                continue
            else:
                break

        if image is not None:
            xsize, ysize, _ = image.shape
            self.__video_output__ = cv2.VideoWriter(self.video_output, self.fourcc, self.fps, (ysize, xsize) )      
            logger.debug(f"Ready to write video to {self.video_output}. Frame: {xsize} {ysize}")

        while self.loop_condition(self.__dict__()):
            try:
                img_encoded = session.recv(self.buffer)
                image_arr = np.frombuffer(img_encoded,np.uint8)
                image = cv2.imdecode(image_arr, cv2.IMREAD_COLOR)
            except Exception as e:
                logger.error(f"Error receiving packets: {e}")
                logger.debug("Waiting for connections after exception ...")
                session, _ = sa.accept()
                logger.debug("Restarting connection...")            
                continue 

            if type(image) is type(None):
                logger.error("Can not read image from socket")
                continue

            xsize, ysize, _ = image.shape
            if image.shape[0] != xsize or image.shape[1] != ysize:
                logger.error(f"Buffer received an image with frame {image.shape[0]}x{image.shape[1]} expected {xsize}x{ysize} ")
                continue

            try:
                logger.debug(f"Image received {image.shape}")
                predict_task = asyncio.create_task( self.predict(img=image) )
                img, results, annotations = await predict_task

                self.status = self.status_filter_foo(annotations) if self.status_filter_foo else self.__status_filter__(annotations)
                if self.draw_foo:
                    image = self.draw_foo( image, results, annotations, self.status ) if self.draw_foo else image 

                self.previous_frame = self.last_frame
                if self.video_output and image is not None: 
                    self.__video_output__.write(image)
                else:
                    logger.debug("Skipt frame for video!")

                self.last_frame = datetime.now()

            except Exception as e:
                logger.error(f"Error predicting or writing image: {e}")
                traceback.print_exc()
                continue
        
        logger.info("Model finished !")