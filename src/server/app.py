import uvicorn
import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from .router import router, public_router
from src.jsBridge import async_worker
from src.utils import logger, resource_path


dist_path = resource_path("wwwroot")
if not os.path.exists(dist_path):
    raise FileNotFoundError(f"文件夹 '{dist_path}' 不存在。")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # on startup: call init_db on the worker and wait for it to complete.
    future = async_worker.submit(async_worker.init_db())
    future.result() # Block until DB is initialized
    logger.info("Database initialization requested by server.")
    yield
    # on shutdown: call disconnect_db on the worker and wait.
    future = async_worker.submit(async_worker.disconnect_db())
    future.result() # Block until DB is disconnected
    logger.info("Database disconnection requested by server.")

app = FastAPI(
    title="vsingerboard",
    description="Multi-platform Singerboard",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan
)

app.include_router(public_router, prefix="/public")


@app.exception_handler(RequestValidationError)
async def exception_handle(request: Request, exc: RequestValidationError):
    logger.error(f"fastapi请求异常：{exc.errors()}")
    return JSONResponse(status_code=200, content={"code": -1, "msg": f"{exc.errors()}", "data": None})


@app.exception_handler(404)
async def redirect_all_requests(request: Request, exc: HTTPException):
    return HTMLResponse(open(Path(dist_path) / "index.html").read())

app.add_middleware(GZipMiddleware, minimum_size=1024)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(router, prefix="/api")
app.mount("/", StaticFiles(directory=dist_path, html=True), name="main")

templates = Jinja2Templates(directory=dist_path)


@app.get("/")
async def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


def startup():
    """
    启动FastAPI应用
    """
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["default"]["fmt"] = "[%(asctime)s][%(levelname)s][%(funcName)s] - %(message)s"
    uvicorn.run(app, host="127.0.0.1", port=8000, log_config=log_config, access_log=False)