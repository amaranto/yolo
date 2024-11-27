import os
from pathlib import Path
from fastapi import APIRouter, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
from urllib.parse import unquote
from config import logging, SPOT, CHANNEL

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Stream output"], prefix="/stream")
url_prefix = f"/{SPOT}/{CHANNEL}"

@router.get( url_prefix + "/prediction/{video_id}")
async def stream_output(video_id: str):

    #paths = sorted(Path(f"output/").iterdir(), key=os.path.getmtime)
    v_name = f"output/{unquote(video_id)}"
    logger.debug(f"Streaming {v_name}")
    def iterfile():   
        with open(v_name, mode="rb") as file_like:   
            yield from file_like

    return StreamingResponse(iterfile(), media_type="video/webm")

@router.get(url_prefix + "/preview")
async def stream_output():
    paths = sorted(Path(f"output/").glob("*.jpg"), key=os.path.getmtime)    

    if not paths:
        return HTMLResponse(content="Image not found", status_code=404)

    def iterfile():   
        with open(paths[0], mode="rb") as file_like:   
            yield from file_like

    return StreamingResponse(iterfile(), media_type="image/jpeg")

@router.get(url_prefix + "/video/{item_id}")
async def stream_output(item_id: str):
    html_content = f'''
    <html>
        <body>
            <video preload="metadata" id="video" src="/stream{url_prefix}/prediction/{item_id}" autoplay="autoplay" />
        </body>
    </html>
    '''
    return HTMLResponse(content=html_content, status_code=200)

@router.get(url_prefix + "/")
async def stream_output():
    paths = sorted(Path(f"output/").glob("*.webm"), key=os.path.getmtime)    

    html_content = f'''
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
    '''

    for path in paths:
        video_name=str(path).split("/")[-1]
        html_content += f'''
        <p>
            <a href="/stream{url_prefix}/video/{video_name}">{video_name}</>
        </p>
        '''

    html_content += '''
        </body>
    </html>
    '''
    return HTMLResponse(content=html_content, status_code=200)

@router.get(url_prefix + "/list")
async def get_content():
    paths = sorted(Path(f"output/").glob("*.webm"), key=os.path.getmtime)    

    videos = []

    for path in paths:
        video_name=str(path).split("/")[-1]
        videos.append({
            "name": video_name,
            "url": f"/stream{url_prefix}/video/{video_name}"
        })

    return JSONResponse(content=jsonable_encoder({"videos": videos}), status_code=status.HTTP_200_OK)