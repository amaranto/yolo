from pydantic import BaseModel
from typing import Set
import numpy as np

class ImageObjTrackingResponse(BaseModel):
    id: int
    label: str
    coords: list[float]
    imgsize:list[int]
    conf: float

class ListImageObjectTrackingResponse(BaseModel):
    annotations: list[ImageObjTrackingResponse]