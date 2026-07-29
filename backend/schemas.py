from typing import TypeVar, Generic, Optional, List

from pydantic import BaseModel, Field

T = TypeVar("T")


class EcsConfigItem(BaseModel):
    regionName: str
    endpoint: str
    projectId: str
    ak: str
    sk: str
    networkZone: Optional[str] = None


class EcsConfigCreateRequest(BaseModel):
    regionName: str
    endpoint: str
    projectId: str
    ak: str
    sk: str
    networkZone: Optional[str] = None


class EcsConfigUpdateRequest(BaseModel):
    regionName: Optional[str] = None
    endpoint: Optional[str] = None
    projectId: Optional[str] = None
    ak: Optional[str] = None
    sk: Optional[str] = None
    networkZone: Optional[str] = None


class SchedulerConfigItem(BaseModel):
    id: Optional[int] = None
    cronExpr: Optional[str] = None
    metricPeriod: Optional[int] = None


class SchedulerConfigUpdateRequest(BaseModel):
    id: int
    cronExpr: Optional[str] = None
    metricPeriod: Optional[int] = None


class CloudVmListRequest(BaseModel):
    department: Optional[str] = None
    appSystem: Optional[str] = None
    hostName: Optional[str] = None
    ipAddress: Optional[str] = None
    status: Optional[str] = None
    cpu: Optional[str] = None
    memory: Optional[str] = None
    systemDiskMin: Optional[int] = None
    systemDiskMax: Optional[int] = None
    dataDiskMin: Optional[int] = None
    dataDiskMax: Optional[int] = None
    pageNum: int = 1
    pageSize: int = 10


class CloudVmItem(BaseModel):
    id: Optional[str] = None
    hostName: Optional[str] = None
    department: Optional[str] = None
    appSystem: Optional[str] = None
    ipAddress: Optional[str] = None
    status: Optional[str] = None
    os: Optional[str] = None
    spec: Optional[str] = None
    architecture: Optional[str] = None
    region: Optional[str] = None
    cpu: Optional[int] = None
    memory: Optional[int] = None
    systemDisk: Optional[int] = None
    dataDisk: Optional[int] = None


class ServerDetailItem(BaseModel):
    id: Optional[str] = None
    hostName: Optional[str] = None
    department: Optional[str] = None
    appSystem: Optional[str] = None
    ipAddress: Optional[str] = None
    ipv6: Optional[str] = None
    publicEip: Optional[str] = None
    status: Optional[str] = None
    os: Optional[str] = None
    osName: Optional[str] = None
    spec: Optional[str] = None
    architecture: Optional[str] = None
    region: Optional[str] = None
    availabilityZone: Optional[str] = None
    cpu: Optional[int] = None
    memory: Optional[int] = None
    systemDisk: Optional[int] = None
    dataDisk: Optional[int] = None
    createdAt: Optional[str] = None
    imageName: Optional[str] = None
    projectId: Optional[str] = None
    regionName: Optional[str] = None
    networkZone: Optional[str] = None
    volumes: Optional[List] = None


class MetricDataPoint(BaseModel):
    timestamp: Optional[str] = None
    cpuUtilMax: Optional[float] = None
    cpuUtilAvg: Optional[float] = None
    cpuUtilMin: Optional[float] = None
    memUtilMax: Optional[float] = None
    memUtilAvg: Optional[float] = None
    memUtilMin: Optional[float] = None
    diskUtilMax: Optional[float] = None
    diskUtilAvg: Optional[float] = None
    diskUtilMin: Optional[float] = None


class ParseRuleItem(BaseModel):
    id: Optional[int] = None
    namePrefix: Optional[str] = None
    departmentIndex: Optional[int] = None
    appSystemIndex: Optional[int] = None
    enabled: Optional[int] = None


class ParseRuleCreateRequest(BaseModel):
    namePrefix: str
    departmentIndex: int = 1
    appSystemIndex: int = 2
    enabled: int = 1


class ParseRuleUpdateRequest(BaseModel):
    id: int
    namePrefix: Optional[str] = None
    departmentIndex: Optional[int] = None
    appSystemIndex: Optional[int] = None
    enabled: Optional[int] = None


class ExportReportRequest(BaseModel):
    startDate: str
    endDate: str
    department: Optional[str] = None
    appSystem: Optional[str] = None
    hostName: Optional[str] = None
    ipAddress: Optional[str] = None
    status: Optional[str] = None
    cpu: Optional[str] = None
    memory: Optional[str] = None
    systemDiskMin: Optional[int] = None
    systemDiskMax: Optional[int] = None
    dataDiskMin: Optional[int] = None
    dataDiskMax: Optional[int] = None


class PageData(BaseModel, Generic[T]):
    list: List[T] = []
    total: int = 0
    pageNum: int = 1
    pageSize: int = 10


class ApiResponse(BaseModel, Generic[T]):
    code: int = 200
    data: Optional[T] = None
    message: Optional[str] = None

    @classmethod
    def success(cls, data: T = None) -> "ApiResponse[T]":
        return cls(code=200, data=data)

    @classmethod
    def error(cls, code: int, message: str) -> "ApiResponse":
        return cls(code=code, message=message)
