import json
import logging
from collections import defaultdict

from sqlalchemy.orm import Session

from models import EcsConfig, EcsServer, EvsVolume
from services.hwcloud_client import hwcloud_get_with_retry

logger = logging.getLogger(__name__)

PAGE_LIMIT = 100


class EvsService:
    def __init__(self, db: Session):
        self.db = db

    def fetch_and_save_volumes(self):
        configs = self.db.query(EcsConfig).all()
        if not configs:
            logger.warning("数据库中无ECS配置信息，跳过EVS云硬盘采集")
            return

        for config in configs:
            logger.info("开始采集EVS云硬盘 regionName=%s, endpoint=%s", config.region_name, config.endpoint)
            all_volumes = []
            marker = None
            has_more = True
            total_count = -1

            while has_more:
                url = config.build_evs_url() + "?limit=" + str(PAGE_LIMIT)
                if marker:
                    url += "&marker=" + marker

                json_str = hwcloud_get_with_retry(config.ak, config.sk, url)
                if not json_str:
                    logger.warning("配置 regionName=%s marker=%s 获取EVS云硬盘列表响应为空", config.region_name, marker)
                    break

                try:
                    response = json.loads(json_str)
                    if total_count < 0 and "count" in response:
                        total_count = response["count"]
                        logger.info("配置 regionName=%s EVS云硬盘总数=%d", config.region_name, total_count)

                    volumes = response.get("volumes")
                    if not volumes:
                        has_more = False
                    else:
                        for dto in volumes:
                            all_volumes.append(self._convert_to_entity(dto, config.project_id))
                        if total_count >= 0 and len(all_volumes) >= total_count:
                            has_more = False
                        elif len(volumes) < PAGE_LIMIT:
                            has_more = False
                        else:
                            marker = volumes[-1].get("id")
                except Exception as e:
                    logger.error("配置 regionName=%s marker=%s 解析EVS云硬盘数据失败: %s", config.region_name, marker, str(e))
                    break

            if all_volumes:
                self._upsert_volumes(all_volumes)
                logger.info("配置 regionName=%s 成功保存 %d 条EVS云硬盘数据", config.region_name, len(all_volumes))

        self.update_server_disk_info()

    def update_server_disk_info(self):
        all_volumes = self.db.query(EvsVolume).all()
        all_servers = self.db.query(EcsServer).all()

        logger.info("EVS云硬盘总数=%d, 云主机总数=%d", len(all_volumes), len(all_servers))

        volumes_by_server = defaultdict(list)
        for vol in all_volumes:
            if vol.server_id:
                volumes_by_server[vol.server_id].append(vol)

        for server in all_servers:
            server_volumes = volumes_by_server.get(server.server_id, [])
            system_disk = 0
            data_disk = 0

            for vol in server_volumes:
                size = vol.size if vol.size else 0
                if self._is_system_disk(vol):
                    system_disk += size
                else:
                    data_disk += size

            server.system_disk = str(system_disk)
            server.data_disk = str(data_disk)

        self.db.commit()
        logger.info("更新 %d 台云主机的系统盘/数据盘信息完成", len(all_servers))

    def _is_system_disk(self, vol: EvsVolume) -> bool:
        return vol.bootable is not None and vol.bootable.lower() == "true"

    def _convert_to_entity(self, dto: dict, project_id: str) -> EvsVolume:
        volume = EvsVolume()
        volume.volume_id = dto.get("id")
        volume.name = dto.get("name")
        volume.status = dto.get("status")
        volume.availability_zone = dto.get("availability_zone")
        volume.created_at = dto.get("created_at")
        volume.updated_at = dto.get("updated_at")
        volume.description = dto.get("description")
        volume.volume_type = dto.get("volume_type")
        volume.size = dto.get("size")
        volume.bootable = dto.get("bootable")
        volume.tenant_id = dto.get("os-vol-tenant-attr:tenant_id") or dto.get("tenant_id")
        volume.user_id = dto.get("user_id")
        volume.service_type = dto.get("service_type")
        volume.multiattach = 1 if dto.get("multiattach") else 0
        volume.dedicated_storage_id = dto.get("dedicated_storage_id")
        volume.dedicated_storage_name = dto.get("dedicated_storage_name")
        volume.wwn = dto.get("wwn")
        volume.serial_number = dto.get("serial_number")
        volume.enterprise_project_id = dto.get("enterprise_project_id")
        volume.project_id = project_id

        metadata = dto.get("metadata")
        if metadata:
            vet = metadata.get("virtual_env_type")
            if vet:
                volume.virtual_env_type = str(vet)

        attachments = dto.get("attachments")
        if attachments and len(attachments) > 0:
            attachment = attachments[0]
            volume.server_id = attachment.get("server_id")
            volume.attachment_id = attachment.get("attachment_id") or attachment.get("id")
            volume.device = attachment.get("device")
            volume.attached_at = attachment.get("attached_at")

        return volume

    def _upsert_volumes(self, volumes: list):
        for volume in volumes:
            existing = self.db.query(EvsVolume).filter_by(volume_id=volume.volume_id).first()
            if existing:
                for col in EvsVolume.__table__.columns:
                    if col.name == "volume_id":
                        continue
                    new_val = getattr(volume, col.name)
                    if new_val is not None:
                        setattr(existing, col.name, new_val)
            else:
                self.db.add(volume)
        self.db.commit()
