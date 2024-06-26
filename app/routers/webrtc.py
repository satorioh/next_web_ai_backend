import uuid
import cv2
from fastapi import APIRouter, Request
from ..utils.log import setup_logger
from ..utils.types import OfferRequest, AnswerResponse
from ..utils.video_helper import VideoTransformTrack
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaRelay

router = APIRouter()
logger = setup_logger(__name__)
pcs = set()
relay = MediaRelay()


@router.post("/offer", response_model=AnswerResponse)
async def handle_offer(req: OfferRequest, request: Request):
    offer = RTCSessionDescription(sdp=req.sdp, type=req.type)

    pc = RTCPeerConnection()
    pc_id = f"PeerConnection({uuid.uuid4()})"
    pcs.add(pc)

    logger.info(f"{pc_id} Created for {request.client.host}")

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        logger.info(f"Connection state is {pc.connectionState}")
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    @pc.on("track")
    def on_track(track):
        logger.info(f"Track {track.kind} received")

        if track.kind == "video":
            pc.addTrack(
                VideoTransformTrack(
                    relay.subscribe(track), transform=req.video_transform
                )
            )

        @track.on("ended")
        async def on_ended():
            logger.info(f"Track {track.kind} ended")

    # handle offer
    await pc.setRemoteDescription(offer)

    # send answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
