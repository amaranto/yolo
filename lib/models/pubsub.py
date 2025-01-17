from pydantic import BaseModel
from concurrent import futures
from google.cloud import pubsub_v1
from typing import Callable
from datetime import datetime, timezone
import json 
import asyncio 

from config import logging

logger = logging.getLogger(__name__)

class PubSubAppV2(BaseModel):
    pod: str
    x: float
    y: float
    w: float
    h: float
    model_type: str
    frame_tmpstmp: str # datetime iso format Z
    class_name: str
    status: dict
    track_id: int
    class_id: int
    conf: float
    spot: int
    channel: int

class PubSubLibrary(BaseModel):
    messages: list[PubSubAppV2]

class PubSubManager():

    def __init__(
            self,
            topic: str,
            project: str
    ):
        self.publisher = pubsub_v1.PublisherClient() 
        self.topic_path = self.publisher.topic_path(project, topic)
        self.publish_futures = []

    def get_callback(
        publish_future: pubsub_v1.publisher.futures.Future, 
        data: str,
        timeout:int = 5
    ) -> Callable[[pubsub_v1.publisher.futures.Future], None]:

        def callback(publish_future: pubsub_v1.publisher.futures.Future) -> None:
            try:
                logger.debug(publish_future.result(timeout=5))
            except futures.TimeoutError:
                logger.error(f"Publishing {data} timed out.")
            except Exception as e:
                logger.error(f"Unknow exception publish message {e}")
        return callback

    async def publish( self, dict_data:dict|None = None, str_data:str|None = None ):

        data = None
        if dict_data:
            data = json.dumps(dict_data, default=str)
        elif str_data:
            data = str_data
        else: 
            error_msg = "No data assigned to pub/sub"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        publish_future = self.publisher.publish(self.topic_path, data.encode("utf-8"))
        # Non-blocking. Publish failures are handled in the callback function.
        publish_future.add_done_callback(self.get_callback(publish_future, data))
        self.publish_futures.append(publish_future)

        # # Wait for all the publish futures to resolve before exiting.
        # futures.wait(publish_futures, return_when=futures.ALL_COMPLETED)

        # print(f"Published messages with error handler to {topic_path}.")

class PostProcessing(PubSubManager):
    def __init__(
            self, 
            topic: str, 
            project: str,
            pod: str,
            channel: int,
            spot: int
        ):
            super().__init__(
                topic,
                project
            )
            self.pod = pod 
            self.channel = channel
            self.spot = spot

    async def post_processing(self, annotations: list[dict], status:dict):
        
        tmstmp = datetime.now(timezone.utc)
        d = tmstmp.isoformat("T").replace('+00:00', 'Z')
        post_processing_tasks = []

        annot_list = [
             PubSubAppV2(
                  pod = self.pod,
                  spot = self.spot,
                  channel = self.channel,
                  x = float(annot["x"]),
                  y = float(annot["y"]),
                  w = float(annot["w"]),
                  h = float(annot["h"]),
                  model_type = status["model"],
                  frame_tmpstmp = d,
                  class_name=annot["class_name"],
                  status={}, # skipping status for the moment
                  track_id=int(annot["track_id"]),
                  class_id=int(annot["class_id"]),
                  conf = float(annot["conf"])
             ) for annot in annotations
        ]
        
        for annot in annot_list:
            post_processing_tasks.append( 
                asyncio.create_task(    
                    self.publish(annot.dict())
                )
            )            
            
        r =  await asyncio.gather(*post_processing_tasks)

        return r    