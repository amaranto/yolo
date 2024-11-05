from fastapi import APIRouter
from fastapi.responses import StreamingResponse, HTMLResponse

router = APIRouter(tags=["Stream output"], prefix="/stream")

@router.get("/prediction")
async def stream_output():
    def iterfile():   
        with open("output/prediction.jpg", mode="rb") as file_like:   
            yield from file_like

    return StreamingResponse(iterfile(), media_type="image/jpeg")

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
            <script>

                var img = document.getElementById("pred");

                setInterval(function() {
                    img.src = "http://localhost:8081/stream/prediction?" + escape(Math.random());
                    
                }, 20);
            </script>        
            <img id="pred"  alt="stream"/>
        </body>
    </html>
    '''
    return HTMLResponse(content=html_content, status_code=200)