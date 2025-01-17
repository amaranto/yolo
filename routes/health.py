from fastapi import APIRouter, UploadFile, status

router = APIRouter(tags=["Health checks"])

@router.get("/healthz",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"status": "Healty."}
    }
)
async def is_healty():
    return {"status": "Healty."}

@router.get("/",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"status": "Healty."}
    }
)
async def is_healty_default():
    return {"status": "Healty."}