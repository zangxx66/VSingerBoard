from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from .router import router
from src.utils import logger
import uvicorn


dist_path = Path(__file__).parent.parent.parent / "wwwroot"
if not dist_path.is_dir():
    dist_path.mkdir()

app = FastAPI(
    title="vsingerboard",
    description="Multi-platform Singerboard",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)


@app.exception_handler(RequestValidationError)
async def exception_handle(request: Request, exc: RequestValidationError):
    logger.error(f"fastapi请求异常：{exc.errors()}")
    return JSONResponse(status_code=200, content={"code": -1, "msg": "请求异常", "data": None})


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
