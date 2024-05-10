from fastapi import APIRouter

router = APIRouter()


@router.get("/getModelLastUpdateTime")
def index():
    return {"Hello": "World"}
