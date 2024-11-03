import requests
import cv2

from lib.tools.yolo import from_yolo_to_p1p2
from lib.models.responses import ListImageObjectTrackingResponse, ImageObjTrackingResponse

# results = model.train(data="coco8.yaml", epochs=100, imgsz=640)
# results = model("path/to/bus.jpg")

cap = cv2.VideoCapture("rtsp://proyecto:proyecto2024@11.37.69.100/cam/realmonitor?channel=9&subtype=1")

if cap.isOpened():
    ret, img= cap.read()
    xSize, ySize, fps = int( cap.get(cv2.CAP_PROP_FRAME_WIDTH) ), int( cap.get(cv2.CAP_PROP_FRAME_HEIGHT) ), 30
    print(f"Size: ({xSize}, {ySize}), FPS:{fps}")
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    out = cv2.VideoWriter('./output/output.mp4', fourcc, fps, (xSize, ySize) )
else:
    raise Exception("Can not connecto to the stream")


while cap.isOpened():
    ret, img= cap.read()


    _, img_encoded = cv2.imencode('.jpg', img)
    files = { "file": img_encoded.tostring() }

    req_response = requests.post("http://localhost:8080/yolo/",files=files )

    if req_response.status_code == 201:
        body = req_response.json()
        for annotation in body["annotations"]:
            
            img_h,img_w, _ = img.shape
            x,y,w,h = annotation["coords"][0], annotation["coords"][1], annotation["coords"][2], annotation["coords"][3]
            p1, p2 = from_yolo_to_p1p2(x,y,w,h, (img_h,img_w) )
            img = cv2.putText(img, f"{annotation['id']}: {annotation['label']}", (p1[0], p1[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (36,255,12))
            img = cv2.rectangle(img, p2, p1, color=(255,0,0))

            out.write(img)
            #cv2.imwrite(f"output/test.jpeg", img)

cap.release()
