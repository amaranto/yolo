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
