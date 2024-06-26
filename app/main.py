from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import model, webrtc
from .config.globals import settings

app = FastAPI(root_path=settings.API_PREFIX)

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
