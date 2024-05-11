from fastapi import APIRouter
from ..utils.types import ModelNameEnum
from ..utils.aws_helper import get_model_last_update_time

router = APIRouter()


@router.get("/getModelLastUpdateTime")
def get_model_time(modelName: ModelNameEnum):
    return get_model_last_update_time(modelName.value)
