from fastapi import APIRouter
from fastapi.responses import StreamingResponse, HTMLResponse

router = APIRouter(tags=["Stream output"], prefix="/stream")

@router.get("/prediction")
async def stream_output():
    def iterfile():   
        with open("output/output.avi", mode="rb") as file_like:   
            yield from file_like

    return StreamingResponse(iterfile(), media_type="video/avi")

@router.get("/original")
async def stream_output():
    def iterfile():   
        with open("output/original.jpg", mode="rb") as file_like:   
            yield from file_like

    return StreamingResponse(iterfile(), media_type="image/jpeg")

@router.get("/")
async def stream_output():
    html_content = '''
    <html>
        <head>
            <title>Some HTML in here</title>

        </head>
        <body>
            <video id="video" src="http://localhost:8081/stream/prediction" autoplay="autoplay" />
        </body>
    </html>
    '''
    return HTMLResponse(content=html_content, status_code=200)