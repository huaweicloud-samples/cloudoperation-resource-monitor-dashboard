import json
import logging

from sqlalchemy.orm import Session

from models import EcsConfig, EcsServer
from services.hwcloud_client import hwcloud_get_with_retry

logger = logging.getLogger(__name__)

PAGE_LIMIT = 100


class EcsService:
    def __init__(self, db: Session):
        self.db = db

    def fetch_and_save_servers(self):
        configs = self.db.query(EcsConfig).all()
        if not configs:
            logger.warning("数据库中无ECS配置信息")
            return

        for config in configs:
            logger.info("开始处理配置 regionName=%s, endpoint=%s", config.region_name, config.endpoint)
            all_servers = []
            marker = None
            has_more = True
            total_count = -1

            while has_more:
                url = config.build_ecs_url() + "?limit=" + str(PAGE_LIMIT)
                if marker:
                    url += "&marker=" + marker

                json_str = hwcloud_get_with_retry(config.ak, config.sk, url)
                if not json_str:
                    logger.warning("配置 regionName=%s marker=%s 获取云主机列表响应为空", config.region_name, marker)
                    break

                try:
                    response = json.loads(json_str)
                    if total_count < 0 and "count" in response:
                        total_count = response["count"]
                        logger.info("配置 regionName=%s 云主机总数=%d", config.region_name, total_count)

                    servers = response.get("servers")
                    if not servers:
                        has_more = False
                    else:
                        for dto in servers:
                            all_servers.append(self._convert_to_entity(dto, config.project_id))
                        if total_count >= 0 and len(all_servers) >= total_count:
                            has_more = False
                        elif len(servers) < PAGE_LIMIT:
                            has_more = False
                        else:
                            marker = servers[-1].get("id")
                except Exception as e:
                    logger.error("配置 regionName=%s marker=%s 解析云主机数据失败: %s", config.region_name, marker, str(e))
                    break

            if all_servers:
                self._upsert_servers(all_servers)
                logger.info("配置 regionName=%s 成功保存 %d 条云主机数据", config.region_name, len(all_servers))

    def _convert_to_entity(self, dto: dict, project_id: str) -> EcsServer:
        server = EcsServer()
        server.project_id = project_id
        server.server_id = dto.get("id")
        server.name = dto.get("name")
        self._parse_name_parts(dto.get("name"), server)
        server.status = dto.get("status")
        server.availability_zone = dto.get("OS-EXT-AZ:availability_zone") or dto.get("availability_zone")
        server.created_at = dto.get("created")
        server.updated = dto.get("updated")
        server.description = dto.get("description")
        server.tenant_id = dto.get("tenant_id")
        server.user_id = dto.get("user_id")
        server.host_id = dto.get("hostId") or dto.get("OS-EXT-SRV-ATTR:host")
        server.vm_state = dto.get("OS-EXT-STS:vm_state") or dto.get("vm_state")
        power_state = dto.get("OS-EXT-STS:power_state")
        server.power_state = str(power_state) if power_state is not None else None
        server.task_state = dto.get("OS-EXT-STS:task_state")
        server.access_ipv4 = dto.get("accessIPv4")
        server.access_ipv6 = dto.get("accessIPv6")
        server.config_drive = dto.get("config_drive")

        self._parse_addresses(dto.get("addresses"), server)

        flavor = dto.get("flavor")
        if flavor:
            server.flavor_id = flavor.get("id")
            server.flavor_name = flavor.get("name")
            server.flavor_vcpus = flavor.get("vcpus")
            server.flavor_ram = flavor.get("ram")

        image = dto.get("image")
        if image:
            server.image_id = image.get("id")

        metadata = dto.get("metadata")
        if metadata:
            server.metadata_enterprise_project_id = metadata.get("enterprise_project_id")
            server.metadata_charging_mode = metadata.get("charging_mode")
            server.os_type = metadata.get("os_type")
            server.os_name = metadata.get("os_name")
            if metadata.get("image_name"):
                server.image_name = metadata.get("image_name")

        fault = dto.get("fault")
        if fault:
            code = fault.get("code")
            server.fault_code = str(code) if code is not None else None
            server.fault_message = fault.get("message")
            server.fault_created = fault.get("created")
            server.fault_details = fault.get("details")

        return server

    def _parse_name_parts(self, name: str, server: EcsServer):
        if not name or not name.startswith("WC_WUH_13_"):
            return
        suffix = name[len("WC_WUH_13_"):]
        parts = suffix.split("_")
        if len(parts) >= 2:
            server.department = parts[0]
            server.app_system = parts[1]

    def _parse_addresses(self, addresses: dict, server: EcsServer):
        if not addresses:
            return
        ipv4_list = []
        ipv6_list = []
        eip_list = []
        for addr_list in addresses.values():
            if not addr_list:
                continue
            for addr in addr_list:
                addr_val = addr.get("addr")
                version = addr.get("version")
                if not addr_val or version is None:
                    continue
                ip_type = addr.get("OS-EXT-IPS:type")
                if version == 4:
                    if ip_type == "floating":
                        eip_list.append(addr_val)
                    elif ip_type == "fixed":
                        ipv4_list.append(addr_val)
                elif version == 6:
                    if ip_type == "fixed":
                        ipv6_list.append(addr_val)
        if ipv4_list:
            server.ip_address = ";".join(ipv4_list)
        if ipv6_list:
            server.ipv6 = ";".join(ipv6_list)
        if eip_list:
            server.public_eip = ";".join(eip_list)

    def _upsert_servers(self, servers: list):
        for server in servers:
            existing = self.db.query(EcsServer).filter_by(server_id=server.server_id).first()
            if existing:
                for col in EcsServer.__table__.columns:
                    if col.name == "server_id":
                        continue
                    new_val = getattr(server, col.name)
                    if new_val is not None:
                        setattr(existing, col.name, new_val)
            else:
                self.db.add(server)
        self.db.commit()
