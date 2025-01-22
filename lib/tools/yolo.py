def from_yolo_to_p1p2(x: int,y: int,w:int,h:int,imgsize:tuple[int,int])->list[(int,int), (int,int)]:
    x = x * imgsize[1]
    y = y * imgsize[0]
    w = w * imgsize[1]/2
    h = h * imgsize[0]/2

    xmin = int(x - w)
    xmax = int(x + w)
    ymin = int(y - h)
    ymax = int(y + h)

    return (xmin, ymin), (xmax, ymax)

def from_p1p2_to_yolo( p1:tuple[int,int], p2:tuple[int,int], imgsize:tuple[int,int])->list[int,int,int,int]:
    x = (p1[0] + p2[0]) / 2 / imgsize[1]
    y = (p1[1] + p2[1]) / 2 / imgsize[0]
    w = (p2[0] - p1[0]) / imgsize[1]
    h = (p2[1] - p1[1]) / imgsize[0]

    return x,y,w,h