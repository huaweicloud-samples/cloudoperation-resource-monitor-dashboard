import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from database import SessionLocal
from services.ecs_service import EcsService
from services.evs_service import EvsService
from services.ces_service import CesService

logger = logging.getLogger(__name__)

_scheduler = None


def _run_scheduled_task():
    db = SessionLocal()
    try:
        logger.info("定时任务执行：开始获取云主机数据，当前时间=%s", datetime.now())
        EcsService(db).fetch_and_save_servers()
        logger.info("定时任务执行：云主机数据获取并保存完成")

        logger.info("定时任务执行：开始获取EVS云硬盘数据，当前时间=%s", datetime.now())
        EvsService(db).fetch_and_save_volumes()
        logger.info("定时任务执行：EVS云硬盘数据获取并保存完成")

        logger.info("定时任务执行：开始获取CES指标列表，当前时间=%s", datetime.now())
        CesService(db).fetch_and_save_metrics()
        logger.info("定时任务执行：CES指标列表获取并保存完成")

        logger.info("定时任务执行：开始采集前一天CES监控数据，当前时间=%s", datetime.now())
        CesService(db).fetch_and_save_metric_data()
        logger.info("定时任务执行：前一天CES监控数据采集并保存完成")

        logger.info("定时任务执行：开始聚合前一天监控日数据，当前时间=%s", datetime.now())
        CesService(db).aggregate_to_daily()
        logger.info("定时任务执行：前一天监控日数据聚合完成")
    except Exception as e:
        logger.error("定时任务执行失败: %s", str(e), exc_info=True)
    finally:
        db.close()


def start_scheduler(cron_expr: str = "0 0 2 * * ?"):
    global _scheduler
    if _scheduler is not None:
        return

    _scheduler = BackgroundScheduler()

    # 解析 cron 表达式：秒 分 时 日 月 ?
    parts = cron_expr.split()
    if len(parts) == 6:
        second, minute, hour, day, month, day_of_week = parts
        trigger = CronTrigger(second=second, minute=minute, hour=hour, day=day, month=month, day_of_week=day_of_week if day_of_week != "?" else None)
    else:
        trigger = CronTrigger(hour=2, minute=0)

    _scheduler.add_job(_run_scheduled_task, trigger, id="hwcloud_scheduled_task", replace_existing=True)
    _scheduler.start()
    logger.info("定时任务调度器已启动，cron=%s", cron_expr)


def shutdown_scheduler():
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("定时任务调度器已停止")
