import logging

from database import SessionLocal
from services.ecs_service import EcsService
from services.evs_service import EvsService
from services.ces_service import CesService

logger = logging.getLogger(__name__)


def run_init_data():
    db = SessionLocal()
    try:
        logger.info("启动初始化：开始获取云主机数据")
        EcsService(db).fetch_and_save_servers()
        logger.info("启动初始化：云主机数据获取并保存完成")

        logger.info("启动初始化：开始获取EVS云硬盘数据")
        EvsService(db).fetch_and_save_volumes()
        logger.info("启动初始化：EVS云硬盘数据获取并保存完成")

        logger.info("启动初始化：开始获取CES指标列表")
        CesService(db).fetch_and_save_metrics()
        logger.info("启动初始化：CES指标列表获取并保存完成")

        logger.info("启动初始化：开始采集前一天CES监控数据")
        CesService(db).fetch_and_save_metric_data()
        logger.info("启动初始化：前一天CES监控数据采集并保存完成")

        logger.info("启动初始化：开始聚合前一天监控日数据")
        CesService(db).aggregate_to_daily()
        logger.info("启动初始化：前一天监控日数据聚合完成")
    except Exception as e:
        logger.error("启动初始化数据采集失败: %s", str(e), exc_info=True)
    finally:
        db.close()
