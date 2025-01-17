from fastapi import APIRouter, UploadFile, status
from lib.models.responses import ImageObjTrackingResponse, ListImageObjectTrackingResponse
from lib.tools.yolo import from_yolo_to_p1p2
from lib.yolo.detector import model
import numpy as np
import cv2

router = APIRouter(tags=["Image Upload and analysis"], prefix="/yolo")

@router.post("/predict",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Successfully Analyzed Image."}
    },
    response_model=ListImageObjectTrackingResponse,
)
async def yolo_image_upload(file: UploadFile) -> ListImageObjectTrackingResponse:
    """Takes a mfrom fastapi import APIRouter, UploadFile, Response, status, HTTPException
ulti-part upload image and runs yolov8 on it to detect objects
    Arguments:
        file (UploadFile): The multi-part upload file
    
    Returns:
        response (ImageAnalysisResponse): The image ID and labels in 
                                          the pydantic object
    
    Examlple cURL:
        curl -X 'POST' \
            'http://localhost/yolo/' \
            -H 'accept: application/json' \
            -H 'Content-Type: multipart/form-data' \
            -F 'file=@image.jpg;type=image/jpeg'
    Example Return:
        [
            {
                id: int,
                label: str,
                coords: list[x,y,w,h],
                imgsize:list[h,w],
                conf: float
            }
        ]
    """

    image_stream = await file.read()

    nparr = np.fromstring(image_stream, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR) 
    results = model.track(img, tracker="bytetrack.yaml", persist=True)
    annotations = []

    for result in results:
        boxes = result.boxes 
        for id, cls, (x,y,w,h), conf in zip(boxes.id, boxes.cls, boxes.xywhn, boxes.conf):

            id = int(id)
            clsId = int(cls)
            clsName = model.names[clsId]
            conf = conf.numpy().round(2)
            
            p1,p2 = from_yolo_to_p1p2(x,y,w,h, (boxes.orig_shape[0], boxes.orig_shape[1]) )
            img = cv2.putText(img, f"{id}: {clsName}", (p1[0], p1[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.3, text_color=(255, 255, 255),text_color_bg=(0,0,0))
            img = cv2.rectangle(img, p2, p1, color=(255,0,0))
            #cv2.imwrite(f"output/predict.jpeg", img)

            annotations.append(            
                ImageObjTrackingResponse(
                    id=id, 
                    label=clsName,
                    coords=[x,y,w,h],
                    imgsize=[boxes.orig_shape[0], boxes.orig_shape[1]],
                    conf=conf
                )
            )

    return ListImageObjectTrackingResponse(
        annotations=annotations
    )