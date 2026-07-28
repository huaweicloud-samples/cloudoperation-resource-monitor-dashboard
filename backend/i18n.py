"""Backend i18n text maps for Excel export and API responses."""

# Status mapping
STATUS_MAP = {
    "zh": {"active": "运行中", "stopped": "已关机", "shutoff": "已关机", "error": "异常", "unknown": "未知"},
    "en": {"active": "Running", "stopped": "Stopped", "shutoff": "Stopped", "error": "Error", "unknown": "Unknown"},
}

# IO label mapping
IO_LABEL_MAP = {
    "zh": {"ultra": "超高IO", "high": "高IO", "normal": "普通IO"},
    "en": {"ultra": "Ultra High IO", "high": "High IO", "normal": "Normal IO"},
}

# Disk type mapping
DISK_TYPE_MAP = {
    "zh": {"system": "系统盘", "data": "数据盘"},
    "en": {"system": "System Disk", "data": "Data Disk"},
}

# Export report headers
EXPORT_HEADERS = {
    "zh": [
        "弹性云服务器ID", "弹性云服务器名称", "弹性云服务器创建时间", "运行状态",
        "所属部门", "所属应用", "所属区域", "所属网络分区",
        "操作系统类型", "镜像ID", "镜像名称", "云主机规格", "CPU架构",
        "CPU(核)", "内存(GB)", "系统盘(GB)", "数据盘(GB)",
        "高IO数据盘(GB)", "超高IO数据盘(GB)", "挂载的云硬盘",
        "项目ID", "domainID", "IPV4地址", "IPV6地址", "region", "弹性公网IP",
        "CPU使用率峰值(%)", "CPU使用率均值(%)", "CPU使用率最小值(%)",
        "内存使用率峰值(%)", "内存使用率均值(%)", "内存使用率最小值(%)",
        "磁盘使用率峰值(%)", "磁盘使用率均值(%)", "磁盘使用率最小值(%)",
    ],
    "en": [
        "ECS ID", "ECS Name", "Created At", "Status",
        "Department", "App System", "Region", "Network Zone",
        "OS Type", "Image ID", "Image Name", "Flavor", "CPU Arch",
        "CPU (cores)", "Memory (GB)", "System Disk (GB)", "Data Disk (GB)",
        "High IO Data Disk (GB)", "Ultra High IO Data Disk (GB)", "Attached Volumes",
        "Project ID", "Domain ID", "IPv4 Address", "IPv6 Address", "Region Endpoint", "Public EIP",
        "CPU Util Max (%)", "CPU Util Avg (%)", "CPU Util Min (%)",
        "Mem Util Max (%)", "Mem Util Avg (%)", "Mem Util Min (%)",
        "Disk Util Max (%)", "Disk Util Avg (%)", "Disk Util Min (%)",
    ],
}

# Export report sheet title and filename
EXPORT_SHEET_TITLE = {"zh": "弹性云服务器报告", "en": "ECS Report"}
EXPORT_FILE_NAME = {"zh": "弹性云服务器报告", "en": "ECS_Report"}

# Metric export headers
METRIC_HEADERS = {
    "zh": [
        "时间", "CPU使用率峰值(%)", "CPU使用率均值(%)", "CPU使用率最小值(%)",
        "内存使用率峰值(%)", "内存使用率均值(%)", "内存使用率最小值(%)",
        "磁盘使用率峰值(%)", "磁盘使用率均值(%)", "磁盘使用率最小值(%)",
    ],
    "en": [
        "Timestamp", "CPU Util Max (%)", "CPU Util Avg (%)", "CPU Util Min (%)",
        "Mem Util Max (%)", "Mem Util Avg (%)", "Mem Util Min (%)",
        "Disk Util Max (%)", "Disk Util Avg (%)", "Disk Util Min (%)",
    ],
}

METRIC_SHEET_TITLE = {"zh": "监控数据", "en": "Metric Data"}
METRIC_FILE_NAME = {"zh": "监控数据", "en": "Metric_Data"}


def get_status(status: str, lang: str = "zh") -> str:
    if not status:
        return STATUS_MAP.get(lang, STATUS_MAP["zh"])["unknown"]
    lower = status.lower()
    return STATUS_MAP.get(lang, STATUS_MAP["zh"]).get(lower, status)


def get_io_label(volume_type: str, lang: str = "zh") -> str:
    labels = IO_LABEL_MAP.get(lang, IO_LABEL_MAP["zh"])
    if volume_type in ("SSD", "ESSD", "ESSD2"):
        return labels["ultra"]
    if volume_type in ("SAS", "GPSSD", "GPSSD2"):
        return labels["high"]
    return labels["normal"]


def get_disk_type(is_system: bool, lang: str = "zh") -> str:
    types = DISK_TYPE_MAP.get(lang, DISK_TYPE_MAP["zh"])
    return types["system"] if is_system else types["data"]
