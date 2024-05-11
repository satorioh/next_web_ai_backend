import asyncio
from fastapi import APIRouter
from ..utils.types import ModelNameEnum
from ..utils.aws_helper import get_model_last_update_time

router = APIRouter()


@router.get("/getModelLastUpdateTime")
async def get_model_time(modelName: ModelNameEnum):
    return await asyncio.to_thread(get_model_last_update_time, modelName.value)
