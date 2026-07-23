from sqlalchemy import Column, String, Integer, Float, Text, PrimaryKeyConstraint
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class EcsConfig(Base):
    __tablename__ = "ecs_config"
    __table_args__ = (
        PrimaryKeyConstraint("region_name", "endpoint", "project_id"),
    )

    region_name = Column(String(64), nullable=False)
    endpoint = Column(String(256), nullable=False)
    project_id = Column(String(64), nullable=False)
    ak = Column(String(256))
    sk = Column(String(256))
    network_zone = Column(String(64))

    def build_ecs_url(self):
        return f"https://ecs.{self.endpoint}/v1/{self.project_id}/cloudservers/detail"

    def build_ces_metrics_url(self):
        return f"https://ces.{self.endpoint}/V1.0/{self.project_id}/metrics"

    def build_ces_batch_query_url(self):
        return f"https://ces.{self.endpoint}/V1.0/{self.project_id}/batch-query-metric-data"

    def build_evs_url(self):
        return f"https://evs.{self.endpoint}/v2/{self.project_id}/cloudvolumes/detail"


class EcsServer(Base):
    __tablename__ = "ecs_server"

    server_id = Column(String(255), primary_key=True)
    name = Column(String(255))
    status = Column(String(64))
    flavor_id = Column(String(255))
    image_id = Column(String(255))
    availability_zone = Column(String(255))
    created_at = Column(String(64))
    updated = Column(String(64))
    description = Column(String(255))
    os_type = Column(String(64))
    os_name = Column(String(255))
    tenant_id = Column(String(64))
    user_id = Column(String(64))
    host_id = Column(String(255))
    vm_state = Column(String(64))
    power_state = Column(String(64))
    task_state = Column(String(255))
    flavor_name = Column(String(64))
    flavor_vcpus = Column(String(64))
    flavor_ram = Column(String(64))
    system_disk = Column(String(64))
    data_disk = Column(String(64))
    image_name = Column(String(255))
    metadata_enterprise_project_id = Column(String(64))
    metadata_charging_mode = Column(String(255))
    access_ipv4 = Column(String(255))
    access_ipv6 = Column(String(512))
    public_eip = Column(String(512))
    config_drive = Column(String(64))
    fault_code = Column(String(64))
    fault_message = Column(String(512))
    fault_created = Column(String(64))
    fault_details = Column(String(64))
    project_id = Column(String(64))
    department = Column(String(128))
    app_system = Column(String(128))


class EvsVolume(Base):
    __tablename__ = "evs_volume"

    volume_id = Column(String(255), primary_key=True)
    name = Column(String(255))
    status = Column(String(64))
    availability_zone = Column(String(255))
    created_at = Column(String(64))
    updated_at = Column(String(64))
    description = Column(String(255))
    volume_type = Column(String(64))
    size = Column(Integer)
    bootable = Column(String(64))
    tenant_id = Column(String(64))
    user_id = Column(String(64))
    service_type = Column(String(64))
    multiattach = Column(Integer)
    dedicated_storage_id = Column(String(255))
    dedicated_storage_name = Column(String(255))
    wwn = Column(String(255))
    serial_number = Column(String(255))
    enterprise_project_id = Column(String(255))
    server_id = Column(String(255))
    attachment_id = Column(String(255))
    device = Column(String(255))
    attached_at = Column(String(64))
    virtual_env_type = Column(String(64))
    project_id = Column(String(64))


class CesMetric(Base):
    __tablename__ = "ces_metric"
    __table_args__ = (
        PrimaryKeyConstraint("namespace", "metric_name", "dimension_name", "dimension_value"),
    )

    namespace = Column(String(64), nullable=False)
    metric_name = Column(String(128), nullable=False)
    dimension_name = Column(String(64), nullable=False)
    dimension_value = Column(String(256), nullable=False)
    unit = Column(String(64))
    endpoint = Column(String(256))
    raw_data = Column(Text)


class CesMetricData(Base):
    __tablename__ = "ces_metric_data"
    __table_args__ = (
        PrimaryKeyConstraint("instance_id", "timestamp"),
    )

    instance_id = Column(String(255), nullable=False)
    timestamp = Column(String(32), nullable=False)
    endpoint = Column(String(64))
    instance_name = Column(String(255))
    cpu_util_max = Column(Float)
    cpu_util_avg = Column(Float)
    cpu_util_min = Column(Float)
    mem_util_max = Column(Float)
    mem_util_avg = Column(Float)
    mem_util_min = Column(Float)
    disk_util_inband_max = Column(Float)
    disk_util_inband_avg = Column(Float)
    disk_util_inband_min = Column(Float)
    cpu_usage_max = Column(Float)
    cpu_usage_avg = Column(Float)
    cpu_usage_min = Column(Float)
    mem_used_percent_max = Column(Float)
    mem_used_percent_avg = Column(Float)
    mem_used_percent_min = Column(Float)
    disk_used_percent_max = Column(Float)
    disk_used_percent_avg = Column(Float)
    disk_used_percent_min = Column(Float)


class CesMetricDataDay(Base):
    __tablename__ = "ces_metric_data_day"
    __table_args__ = (
        PrimaryKeyConstraint("instance_id", "timestamp"),
    )

    instance_id = Column(String(255), nullable=False)
    timestamp = Column(String(32), nullable=False)
    endpoint = Column(String(64))
    instance_name = Column(String(255))
    cpu_util_max = Column(Float)
    cpu_util_avg = Column(Float)
    cpu_util_min = Column(Float)
    mem_util_max = Column(Float)
    mem_util_avg = Column(Float)
    mem_util_min = Column(Float)
    disk_util_inband_max = Column(Float)
    disk_util_inband_avg = Column(Float)
    disk_util_inband_min = Column(Float)
    cpu_usage_max = Column(Float)
    cpu_usage_avg = Column(Float)
    cpu_usage_min = Column(Float)
    mem_used_percent_max = Column(Float)
    mem_used_percent_avg = Column(Float)
    mem_used_percent_min = Column(Float)
    disk_used_percent_max = Column(Float)
    disk_used_percent_avg = Column(Float)
    disk_used_percent_min = Column(Float)
