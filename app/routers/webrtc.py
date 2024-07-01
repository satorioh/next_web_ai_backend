import asyncio
import time
import uuid
import psutil
from fastapi import APIRouter, Request
from ..utils.log import setup_logger
from ..utils.types import OfferRequest, AnswerResponse
from ..utils.video_helper import VideoTransformTrack
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaRelay

router = APIRouter()
logger = setup_logger(__name__)
pcs = dict()
relay = MediaRelay()
CHECK_CONNECTIONS_INTERVAL = 60  # 5min,检查连接的时间间隔
MAX_CONNECTION_TIME = 900  # 15min,最大连接时间
CPU_THRESHOLD = 80  # CPU利用率阈值


@router.post("/offer", response_model=AnswerResponse)
async def handle_offer(req: OfferRequest, request: Request):
    if psutil.cpu_percent() > CPU_THRESHOLD:
        return {"sdp": "", "type": ""}
    offer = RTCSessionDescription(sdp=req.sdp, type=req.type)

    pc = RTCPeerConnection()
    pc_id = f"PeerConnection({uuid.uuid4()})"
    start_time = time.time()
    pcs[pc_id] = {"pc": pc, "start_time": start_time}

    logger.info(f"{pc_id} Created for {request.client.host}")

    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        def on_message(message):
            # logger.info(f"Data channel message: {message}")
            pcs[pc_id]["channel"] = channel  # 保存datachannel的引用
            if isinstance(message, str) and message.startswith("ping"):
                channel.send("pong" + message[4:] + f" {psutil.cpu_percent()} {len(pcs)}")

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        logger.info(f"{pc_id} is {pc.connectionState}")
        match pc.connectionState:
            case "connected":
                pass
            case "failed" | "closed":
                await pc.close()
                pcs.pop(pc_id)
                logger.info(f"pcs length -> {len(pcs)}")
            case _:
                pass

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


async def check_connections():
    while True:
        logger.info(f"Checking connections -> {len(pcs)}")
        await asyncio.sleep(CHECK_CONNECTIONS_INTERVAL)
        if len(pcs) == 0:
            continue
        now = time.time()
        for pc_id, value in list(pcs.items()):  # 使用list创建一个副本，以避免在迭代过程中修改字典
            if now - value['start_time'] > MAX_CONNECTION_TIME:
                channel = value.get('channel')
                if channel:
                    channel.send("timeout")  # 发送消息
                await value['pc'].close()  # 关闭RTCPeerConnection
                logger.info(f"{pc_id} has been removed due to timeout.")


async def on_shutdown():
    coros = [value["pc"].close() for value in pcs.values()]
    await asyncio.gather(*coros)
    pcs.clear()
    logger.info(f"All peer connections are closed -> {pcs}")
