import uvicorn
import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from .router import router
from src.database import Db
from src.utils import logger, resource_path, IPCManager
from . import ipc_instance


dist_path = resource_path("wwwroot", False)
_token = ""
if not os.path.exists(dist_path):
    raise FileNotFoundError(f"文件夹 '{dist_path}' 不存在。")


def verify_token(request: Request):
    x_token = request.headers.get("x-token")
    if x_token != _token and request.url.path != "/danamu":
        raise HTTPException(status_code=500, detail="Authentication error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Database initialization will be handled by async_worker
    await Db.init()
    logger.info("Database initialization completed.")
    yield
    # Database disconnection will be handled by async_worker
    await Db.disconnect()
    ipc_instance.ipc_manager.send_message("exit")
    ipc_instance.ipc_manager.close()
    logger.info("Database disconnection completed.")

app = FastAPI(
    title="vsingerboard",
    description="Multi-platform Singerboard",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan,
    dependencies=[Depends(verify_token)],
)


@app.exception_handler(RequestValidationError)
async def exception_handle(request: Request, exc: RequestValidationError):
    logger.error(f"fastapi请求异常：{exc.errors()}，{request.url}")
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


def startup(token: str, ipc_manager: IPCManager):
    """
    启动FastAPI应用
    """
    global _token
    try:
        _token = token
        ipc_instance.ipc_manager = ipc_manager
        log_config = uvicorn.config.LOGGING_CONFIG
        log_config["formatters"]["default"]["fmt"] = "[%(asctime)s][%(levelname)s][%(funcName)s] - %(message)s"
        uvicorn.run(app, host="127.0.0.1", port=8000, log_config=log_config, access_log=False)
    except Exception as e:
        logger.error(e)
