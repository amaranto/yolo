import cv2
from lib.tools.yolo import from_yolo_to_p1p2
from config import logging
logger = logging.getLogger(__name__)

def draw_bboxes(image, msgs:list[dict], p1: tuple[int,int], p2: tuple[int,int]|None=None,font:int = cv2.FONT_HERSHEY_SIMPLEX, font_scale: float=1.0):

    text_position = (p1[0], p1[1]+10)     
    max_text_width = 0

    for msg in msgs:
        line = msg["text"]
        font_color = msg["color"] if "color" in msg else (255,255,255)        
        text_description = line
        text_size, _ = cv2.getTextSize(text_description, font, font_scale, 1)
        text_w, text_h = text_size 
        text_w = text_w if text_w > max_text_width else max_text_width
        image = cv2.rectangle(image, text_position, (text_position[0]+text_w, text_position[1]-text_h ), (0,0,0), -1)
        image = cv2.putText(image, text_description, text_position, font, font_scale, font_color, 1)
        text_position=(text_position[0], text_position[1]+ text_h + 1)
        
        # If p2 is not defined only draw bbox with description
        if p2:
            image = cv2.rectangle(image, p2, p1, color=(255,0,0))    
    
    return image

# def draw_tracking_counting_model(image, result, annotations, status ):
#     for annotation in annotations:
#         p1,p2 = from_yolo_to_p1p2(
#             annotation["x"],
#             annotation["y"],
#             annotation["w"],
#             annotation["h"], 
#             (image.shape[0], image.shape[1]) 
#         )

#         conf = annotation['conf']
#         track_id = annotation['track_id']
#         class_name = 'motorcycle' if annotation['class_name'] == "bicycle" else annotation['class_name']
#         text = f"{track_id}: {class_name} {conf}"
#         color = class_colors[class_name] if class_name in class_colors else class_colors["default"]
#         image = draw_bboxes(image, [{"text": text, "color": color}], p1,p2, font_scale=0.3)
        
#     image = draw_bboxes(
#         image, 
#         [ 
#             {
#                 "text": f"{k} {v["total"]}",
#                 "color": class_colors[k] if k in class_colors else class_colors["default"]
#             }
#             for k,v in status["classes"].items() 
#         ], 
#         (0,0), 
#         font_scale=0.5
#     )
    
#     return image

# def draw_tracking_charge_model(image, result, annotations, status ):
#     classes = [
#         "truck",
#         "bus",
#         "car",
#         "cono",
#         "person",
#         "valde",
#         "extintor"
#     ]

#     output=None

#     for annotation in annotations:
#         p1,p2 = from_yolo_to_p1p2(
#             annotation["x"],
#             annotation["y"],
#             annotation["w"],
#             annotation["h"], 
#             (image.shape[0], image.shape[1]) 
#         )

#         conf = annotation['conf']
#         track_id = annotation['track_id']
#         class_name = annotation['class_name']
#         if class_name in classes:
#             output = draw_bboxes(
#                 image, 
#                 [{ 
#                     "text": f"{track_id}: {class_name} {conf}",
#                     "color": class_colors[class_name] if class_name in class_colors else class_colors["default"]
#                 }], 
#                 p1,p2, 
#                 font_scale=0.3
#             )

#     if output is not None:    
#         output = draw_bboxes(
#             output, 
#             [ 
#                 {
#                     "text": f"{cls}",
#                     "color": (0,255,0) if cls in status["classes"] else (0,0,255)
#                 } 
#                 for cls in classes 
#             ], 
#             (0,0), 
#             font_scale=0.5, 
#         )

#     return  output