import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .routers import model, webrtc
from .config.globals import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        asyncio.ensure_future(webrtc.check_connections())
        yield
        await webrtc.on_shutdown()
    finally:
        pass


app = FastAPI(root_path=settings.API_PREFIX, lifespan=lifespan)

origins = [
    "http://localhost:3000",
    "https://next.regulusai.top",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(model.router, prefix="/model", tags=["model"])
app.include_router(webrtc.router, prefix="/webrtc", tags=["webrtc"])
