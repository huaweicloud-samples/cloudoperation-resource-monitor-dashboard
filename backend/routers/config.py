import logging
import threading

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from models import EcsConfig
from schemas import (
    EcsConfigItem, EcsConfigCreateRequest, EcsConfigUpdateRequest,
    ApiResponse,
)
from services.ecs_service import EcsService
from services.evs_service import EvsService
from services.ces_service import CesService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/config", tags=["config"])


def _to_config_item(config: EcsConfig) -> EcsConfigItem:
    return EcsConfigItem(
        regionName=config.region_name,
        endpoint=config.endpoint,
        projectId=config.project_id,
        ak=config.ak,
        sk=config.sk,
        networkZone=config.network_zone,
    )


@router.get("/list")
def list_configs(db: Session = Depends(get_db)):
    configs = db.query(EcsConfig).all()
    items = [_to_config_item(c) for c in configs]
    return ApiResponse.success(items)


@router.post("/add")
def add_config(request: EcsConfigCreateRequest, db: Session = Depends(get_db)):
    existing = db.query(EcsConfig).filter_by(
        region_name=request.regionName,
        endpoint=request.endpoint,
        project_id=request.projectId,
    ).first()
    if existing:
        return ApiResponse.error(400, "该鉴权配置已存在")

    config = EcsConfig(
        region_name=request.regionName,
        endpoint=request.endpoint,
        project_id=request.projectId,
        ak=request.ak,
        sk=request.sk,
        network_zone=request.networkZone,
    )
    db.add(config)
    db.commit()
    return ApiResponse.success(_to_config_item(config))


@router.put("/update")
def update_config(request: EcsConfigUpdateRequest, db: Session = Depends(get_db)):
    # Use original keys to find the record; we need at least the old keys
    # For simplicity, require all three primary key fields
    if not request.regionName or not request.endpoint or not request.projectId:
        return ApiResponse.error(400, "缺少主键字段(regionName/endpoint/projectId)")

    config = db.query(EcsConfig).filter_by(
        region_name=request.regionName,
        endpoint=request.endpoint,
        project_id=request.projectId,
    ).first()
    if not config:
        return ApiResponse.error(404, "鉴权配置不存在")

    if request.ak is not None:
        config.ak = request.ak
    if request.sk is not None:
        config.sk = request.sk
    if request.networkZone is not None:
        config.network_zone = request.networkZone

    db.commit()
    return ApiResponse.success(_to_config_item(config))


@router.delete("/delete")
def delete_config(
    regionName: str = Query(...),
    endpoint: str = Query(...),
    projectId: str = Query(...),
    db: Session = Depends(get_db),
):
    config = db.query(EcsConfig).filter_by(
        region_name=regionName,
        endpoint=endpoint,
        project_id=projectId,
    ).first()
    if not config:
        return ApiResponse.error(404, "鉴权配置不存在")

    db.delete(config)
    db.commit()
    return ApiResponse.success("删除成功")


@router.post("/refresh")
def refresh_config_resources(
    regionName: str = Query(...),
    endpoint: str = Query(...),
    projectId: str = Query(...),
    db: Session = Depends(get_db),
):
    config = db.query(EcsConfig).filter_by(
        region_name=regionName,
        endpoint=endpoint,
        project_id=projectId,
    ).first()
    if not config:
        return ApiResponse.error(404, "鉴权配置不存在")

    def _run_refresh():
        refresh_db = None
        try:
            from database import SessionLocal
            refresh_db = SessionLocal()
            logger.info("按租户刷新资源 regionName=%s projectId=%s", config.region_name, config.project_id)

            EcsService(refresh_db).fetch_and_save_servers()
            logger.info("按租户刷新：云主机数据获取完成")

            EvsService(refresh_db).fetch_and_save_volumes()
            logger.info("按租户刷新：云硬盘数据获取完成")

            CesService(refresh_db).fetch_and_save_metrics()
            logger.info("按租户刷新：CES指标列表获取完成")

            CesService(refresh_db).fetch_and_save_metric_data()
            logger.info("按租户刷新：CES监控数据采集完成")

            CesService(refresh_db).aggregate_to_daily()
            logger.info("按租户刷新：监控日数据聚合完成")
        except Exception as e:
            logger.error("按租户刷新资源失败: %s", str(e), exc_info=True)
        finally:
            if refresh_db:
                refresh_db.close()

    thread = threading.Thread(target=_run_refresh, daemon=True)
    thread.start()

    return ApiResponse.success("刷新任务已启动，请稍后查看数据更新")
