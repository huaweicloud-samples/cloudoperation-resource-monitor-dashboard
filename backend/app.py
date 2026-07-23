import logging
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import SERVER_PORT, SCHEDULER_CRON
from database import init_db
from init_data import run_init_data
from scheduler import start_scheduler, shutdown_scheduler
from routers import cloud_vm, config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("应用启动中...")
    init_db()
    # 在后台线程中执行初始化数据采集，不阻塞服务启动
    init_thread = threading.Thread(target=run_init_data, daemon=True)
    init_thread.start()
    start_scheduler(SCHEDULER_CRON)
    logger.info("应用启动完成")
    yield
    # Shutdown
    shutdown_scheduler()
    logger.info("应用已停止")


app = FastAPI(title="HuaweiCloud Resource Monitor Dashboard", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cloud_vm.router)
app.include_router(config.router)


@app.get("/hello")
def hello():
    return "helloworld"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=SERVER_PORT)
