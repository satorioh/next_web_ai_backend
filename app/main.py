from fastapi import FastAPI
from .routers import model
from .config.globals import settings

app = FastAPI(root_path=settings.API_PREFIX)

app.include_router(model.router, prefix="/model", tags=["model"])
