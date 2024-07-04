from pydantic import BaseModel
from typing import Optional
from enum import Enum


class ModelNameEnum(str, Enum):
    rps = "rps"
    vos = "vos"


class OfferRequest(BaseModel):
    sdp: str
    type: str
    video_transform: str


class AnswerResponse(BaseModel):
    sdp: str
    type: str
    errorMsg: Optional[str] = None
