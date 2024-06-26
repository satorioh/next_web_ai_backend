from pydantic import BaseModel
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
