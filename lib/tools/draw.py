import cv2
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
