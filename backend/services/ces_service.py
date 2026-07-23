import json
import logging
from collections import defaultdict, OrderedDict
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from models import EcsConfig, EcsServer, CesMetric, CesMetricData, CesMetricDataDay
from services.hwcloud_client import hwcloud_get_with_retry, hwcloud_post_with_retry

logger = logging.getLogger(__name__)

MAX_METRICS_PER_REQUEST = 10
ONE_DAY_MS = 24 * 3600 * 1000
MAX_REQUEST_BODY_KB = 512
CES_PAGE_LIMIT = 1000


class _MetricAggregate:
    __slots__ = ("max", "avg", "min", "partitions")

    def __init__(self):
        self.max = None
        self.avg = None
        self.min = None
        self.partitions = {}

    def add_metric_data(self, dp: dict, filter_type: str):
        if filter_type == "max" and dp.get("max") is not None:
            self.max = dp["max"]
        if filter_type == "average" and dp.get("average") is not None:
            self.avg = dp["average"]
        if filter_type == "min" and dp.get("min") is not None:
            self.min = dp["min"]

    def add_disk_data(self, metric_name: str, partition_name: str, dp: dict, filter_type: str):
        partition = self.partitions.setdefault(partition_name, _DiskPartition())
        if metric_name.endswith("_disk_used"):
            if filter_type == "max" and dp.get("max") is not None:
                partition.used_max = dp["max"]
            if filter_type == "average" and dp.get("average") is not None:
                partition.used_avg = dp["average"]
            if filter_type == "min" and dp.get("min") is not None:
                partition.used_min = dp["min"]
        if metric_name.endswith("_disk_total"):
            if filter_type == "max" and dp.get("max") is not None:
                partition.total_max = dp["max"]
            if filter_type == "average" and dp.get("average") is not None:
                partition.total_avg = dp["average"]
            if filter_type == "min" and dp.get("min") is not None:
                partition.total_min = dp["min"]
        if metric_name.endswith("_disk_usedPercent"):
            if filter_type == "max" and dp.get("max") is not None:
                partition.used_percent_max = dp["max"]
            if filter_type == "average" and dp.get("average") is not None:
                partition.used_percent_avg = dp["average"]
            if filter_type == "min" and dp.get("min") is not None:
                partition.used_percent_min = dp["min"]


class _DiskPartition:
    __slots__ = (
        "used_max", "used_avg", "used_min",
        "total_max", "total_avg", "total_min",
        "used_percent_max", "used_percent_avg", "used_percent_min",
    )

    def __init__(self):
        self.used_max = None
        self.used_avg = None
        self.used_min = None
        self.total_max = None
        self.total_avg = None
        self.total_min = None
        self.used_percent_max = None
        self.used_percent_avg = None
        self.used_percent_min = None


class CesService:
    def __init__(self, db: Session):
        self.db = db

    # ==================== 指标列表采集 ====================

    def fetch_and_save_metrics(self):
        configs = self.db.query(EcsConfig).all()
        if not configs:
            logger.warning("数据库中无ECS配置信息，跳过CES指标列表采集")
            return
        for config in configs:
            logger.info("开始采集CES指标列表，配置 regionName=%s, endpoint=%s", config.region_name, config.endpoint)
            self._fetch_and_save_metrics_for_config(config)

    def _fetch_and_save_metrics_for_config(self, config: EcsConfig):
        all_metrics = []
        start = ""
        has_more = True

        while has_more:
            url = config.build_ces_metrics_url() + "&limit=" + str(CES_PAGE_LIMIT) + "&namespace=AGT.ECS"
            if start:
                url += "&start=" + start

            json_str = hwcloud_get_with_retry(config.ak, config.sk, url)
            if not json_str:
                logger.warning("配置 regionName=%s CES指标列表响应为空", config.region_name)
                break

            try:
                response = json.loads(json_str)
                page_metrics = self._parse_metrics(response, config.endpoint)
                all_metrics.extend(page_metrics)

                meta_data = response.get("meta_data")
                if meta_data and meta_data.get("marker") and meta_data.get("count") and meta_data["count"] >= CES_PAGE_LIMIT:
                    start = meta_data["marker"]
                else:
                    has_more = False
            except Exception as e:
                logger.error("配置 regionName=%s 解析CES指标列表失败: %s", config.region_name, str(e))
                break

        if all_metrics:
            self._upsert_metrics(all_metrics)
            logger.info("配置 regionName=%s 成功保存 %d 条CES指标数据", config.region_name, len(all_metrics))

    def _parse_metrics(self, response: dict, endpoint: str) -> list:
        result = []
        metrics = response.get("metrics")
        if not metrics:
            return result
        for dto in metrics:
            metric_name = dto.get("metric_name", "")
            if not (metric_name.endswith("_disk_usedPercent") or metric_name.endswith("_disk_used")
                    or metric_name.endswith("_disk_total") or metric_name.endswith("_disk_free")):
                continue
            dimensions = dto.get("dimensions")
            if not dimensions:
                continue
            instance_id = None
            mount_point = None
            for dim in dimensions:
                if dim.get("name") == "instance_id":
                    instance_id = dim.get("value")
                elif dim.get("name") == "mount_point":
                    mount_point = dim.get("value")
            if not instance_id:
                continue

            metric = CesMetric()
            metric.namespace = dto.get("namespace")
            metric.metric_name = metric_name
            metric.unit = dto.get("unit")
            metric.dimension_name = "instance_id"
            metric.dimension_value = f"{instance_id}|{mount_point}" if mount_point else instance_id
            metric.endpoint = endpoint
            metric.raw_data = self._build_raw_data(dto)
            result.append(metric)
        return result

    def _build_raw_data(self, dto: dict) -> str:
        try:
            raw = {
                "namespace": dto.get("namespace"),
                "metric_name": dto.get("metric_name"),
                "dimensions": [{"name": d.get("name"), "value": d.get("value")} for d in (dto.get("dimensions") or [])],
            }
            return json.dumps(raw, ensure_ascii=False)
        except Exception as e:
            logger.error("构建rawData失败: %s", str(e))
            return None

    # ==================== 监控采样数据采集 ====================

    def fetch_and_save_metric_data(self, from_ts: int = None, to_ts: int = None, server_id: str = None):
        if from_ts is None or to_ts is None:
            yesterday = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
            from_ts = int(yesterday.timestamp() * 1000)
            to_ts = from_ts + ONE_DAY_MS

        if server_id:
            self._fetch_and_save_metric_data_single(from_ts, to_ts, server_id)
        else:
            self._fetch_and_save_metric_data_all(from_ts, to_ts)

    def _fetch_and_save_metric_data_all(self, from_ts: int, to_ts: int):
        configs = self.db.query(EcsConfig).all()
        if not configs:
            logger.warning("数据库中无ECS配置信息，跳过CES监控数据采集")
            return
        for config in configs:
            logger.info("开始采集CES监控数据，配置 regionName=%s, endpoint=%s", config.region_name, config.endpoint)
            servers = self.db.query(EcsServer).filter_by(project_id=config.project_id).all()
            if not servers:
                logger.warning("配置 projectId=%s 下无云主机数据，跳过", config.project_id)
                continue
            self._fetch_and_save_for_config(config, servers, from_ts, to_ts, False)

    def _fetch_and_save_metric_data_single(self, from_ts: int, to_ts: int, server_id: str):
        server = self.db.query(EcsServer).filter_by(server_id=server_id).first()
        if not server:
            logger.warning("未找到云主机 serverId=%s", server_id)
            return
        config = self.db.query(EcsConfig).filter_by(project_id=server.project_id).first()
        if not config:
            logger.warning("未找到云主机 serverId=%s 对应的配置", server_id)
            return
        logger.info("单独采集云主机监控数据，serverId=%s, name=%s, regionName=%s", server_id, server.name, config.region_name)
        self._fetch_and_save_for_config(config, [server], from_ts, to_ts, True)

    def _fetch_and_save_for_config(self, config: EcsConfig, servers: list, from_ts: int, to_ts: int, verbose: bool):
        metric_infos = self._build_all_metric_infos(servers, config.endpoint)
        if not metric_infos:
            logger.warning("无有效监控指标，跳过")
            return

        server_name_map = {s.server_id: s.name for s in servers}

        batches = self._split_into_batches(metric_infos)
        logger.info("配置 regionName=%s 指标总数=%d 分为%d批(每批最多%d指标)", config.region_name, len(metric_infos), len(batches), MAX_METRICS_PER_REQUEST)

        day_segments = self._split_time_range_by_day(from_ts, to_ts)
        logger.info("配置 regionName=%s 时间范围分为%d天段", config.region_name, len(day_segments))

        for seg_idx, (seg_from, seg_to) in enumerate(day_segments):
            seg_date = datetime.fromtimestamp(seg_from / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
            seg_total_count = 0

            seg_agg = defaultdict(lambda: defaultdict(dict))

            for batch_idx, batch_metrics in enumerate(batches):
                filters = ["max", "average", "min"]

                for filter_type in filters:
                    request_body = {
                        "metrics": batch_metrics,
                        "period": "300",
                        "filter": filter_type,
                        "from": seg_from,
                        "to": seg_to,
                    }
                    try:
                        body_str = json.dumps(request_body, ensure_ascii=False)

                        if len(body_str.encode("utf-8")) > MAX_REQUEST_BODY_KB * 1024:
                            logger.warning("第%d批请求体超过%dKB，跳过", batch_idx + 1, MAX_REQUEST_BODY_KB)
                            continue

                        json_str = hwcloud_post_with_retry(config.ak, config.sk, config.build_ces_batch_query_url(), body_str)
                        if not json_str:
                            continue

                        self._parse_and_aggregate_metric_data(json_str, filter_type, seg_agg)
                    except Exception as e:
                        logger.error("配置 regionName=%s filter=%s batch=%d segFrom=%d 采集CES监控数据失败: %s",
                                     config.region_name, filter_type, batch_idx + 1, seg_from, str(e))

                logger.info("配置 regionName=%s 日期=%s 批次%d/%d 采集完成", config.region_name, seg_date, batch_idx + 1, len(batches))

            seg_data_list = self._build_metric_data_list(seg_agg, config.endpoint, server_name_map)
            if seg_data_list:
                self._upsert_metric_data(seg_data_list)
                seg_total_count += len(seg_data_list)

            logger.info("日期=%s 入库完成 共计入库%d条数据", seg_date, seg_total_count)

    def _build_all_metric_infos(self, servers: list, endpoint: str) -> list:
        metric_infos = []
        for server in servers:
            instance_dim = {"name": "instance_id", "value": server.server_id}

            self._add_metric_info(metric_infos, "SYS.ECS", "cpu_util", [instance_dim])
            self._add_metric_info(metric_infos, "SYS.ECS", "mem_util", [instance_dim])
            self._add_metric_info(metric_infos, "SYS.ECS", "disk_util_inband", [instance_dim])
            self._add_metric_info(metric_infos, "AGT.ECS", "cpu_usage", [instance_dim])
            self._add_metric_info(metric_infos, "AGT.ECS", "mem_usedPercent", [instance_dim])

            server_disk_metrics = self.db.query(CesMetric).filter(
                CesMetric.endpoint == endpoint,
                CesMetric.dimension_value.like(f"{server.server_id}%")
            ).all()

            added_disk_keys = set()
            disk_metric_count = 0
            for dm in server_disk_metrics:
                if not dm.metric_name:
                    continue
                if not (dm.metric_name.endswith("_disk_used") or dm.metric_name.endswith("_disk_total")
                        or dm.metric_name.endswith("_disk_usedPercent")):
                    continue
                disk_metric_count += 1
                disk_key = f"{dm.metric_name}_{dm.dimension_value}"
                if disk_key not in added_disk_keys:
                    added_disk_keys.add(disk_key)
                    dims = self._parse_dimensions_from_raw_data(dm.raw_data) if dm.raw_data else None
                    if not dims:
                        dims = [instance_dim]
                    self._add_metric_info(metric_infos, "AGT.ECS", dm.metric_name, dims)

            if disk_metric_count == 0:
                logger.warning("主机 serverId=%s name=%s 在ces_metric表中无磁盘指标记录", server.server_id, server.name)

        return metric_infos

    def _add_metric_info(self, list_: list, namespace: str, metric_name: str, dimensions: list):
        list_.append({
            "namespace": namespace,
            "metric_name": metric_name,
            "dimensions": dimensions,
        })

    def _parse_dimensions_from_raw_data(self, raw_data: str) -> list:
        try:
            info = json.loads(raw_data)
            dims = info.get("dimensions")
            if dims:
                return [{"name": d.get("name"), "value": d.get("value")} for d in dims]
        except Exception as e:
            logger.error("解析rawData中的dimensions失败: %s", str(e))
        return None

    def _split_into_batches(self, metric_infos: list) -> list:
        by_server = OrderedDict()
        for mi in metric_infos:
            server_id = mi["dimensions"][0]["value"] if mi.get("dimensions") else ""
            by_server.setdefault(server_id, []).append(mi)
        batches = []
        for server_metrics in by_server.values():
            for i in range(0, len(server_metrics), MAX_METRICS_PER_REQUEST):
                batches.append(server_metrics[i:i + MAX_METRICS_PER_REQUEST])
        return batches

    def _split_time_range_by_day(self, from_ts: int, to_ts: int) -> list:
        segments = []
        seg_from = from_ts
        while seg_from < to_ts:
            seg_to = min(seg_from + ONE_DAY_MS, to_ts)
            segments.append((seg_from, seg_to))
            seg_from = seg_to
        return segments

    def _parse_and_aggregate_metric_data(self, json_str: str, filter_type: str, server_agg: dict):
        try:
            response = json.loads(json_str)
            metrics = response.get("metrics")
            if not metrics:
                return

            for metric_dto in metrics:
                dimensions = metric_dto.get("dimensions")
                instance_id = dimensions[0].get("value") if dimensions else None
                if not instance_id:
                    continue

                metric_name = metric_dto.get("metric_name", "")
                datapoints = metric_dto.get("datapoints")
                if not datapoints:
                    continue

                namespace = metric_dto.get("namespace", "")
                for dp in datapoints:
                    ts = dp.get("timestamp")
                    if ts is None:
                        continue

                    if namespace == "AGT.ECS" and (metric_name.endswith("_disk_used") or metric_name.endswith("_disk_total") or metric_name.endswith("_disk_usedPercent")):
                        partition_name = self._extract_mount_point(metric_name)
                        disk_key = f"disk_{partition_name}"
                        agg = server_agg[instance_id][ts].setdefault(disk_key, _MetricAggregate())
                        agg.add_disk_data(metric_name, partition_name, dp, filter_type)
                    else:
                        agg_key = f"{namespace}.{metric_name}"
                        agg = server_agg[instance_id][ts].setdefault(agg_key, _MetricAggregate())
                        agg.add_metric_data(dp, filter_type)
        except Exception as e:
            logger.error("解析并聚合CES监控数据失败: %s", str(e))

    def _extract_mount_point(self, metric_name: str) -> str:
        idx = metric_name.find("_disk_")
        if idx <= 0:
            return "default"
        prefix = metric_name[:idx]
        if not prefix:
            return "/"
        return prefix.replace("SlAsH", "/")

    def _build_metric_data_list(self, server_agg: dict, endpoint: str, server_name_map: dict) -> list:
        result = []
        for instance_id, ts_map in server_agg.items():
            for ts, aggs in ts_map.items():
                data = CesMetricData()
                data.endpoint = endpoint
                data.instance_id = instance_id
                data.instance_name = server_name_map.get(instance_id, "")
                data.timestamp = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")

                cpu_util = aggs.get("SYS.ECS.cpu_util")
                if cpu_util:
                    data.cpu_util_max = cpu_util.max
                    data.cpu_util_avg = cpu_util.avg
                    data.cpu_util_min = cpu_util.min

                mem_util = aggs.get("SYS.ECS.mem_util")
                if mem_util:
                    data.mem_util_max = mem_util.max
                    data.mem_util_avg = mem_util.avg
                    data.mem_util_min = mem_util.min

                disk_util_inband = aggs.get("SYS.ECS.disk_util_inband")
                if disk_util_inband:
                    data.disk_util_inband_max = disk_util_inband.max
                    data.disk_util_inband_avg = disk_util_inband.avg
                    data.disk_util_inband_min = disk_util_inband.min

                cpu_usage = aggs.get("AGT.ECS.cpu_usage")
                if cpu_usage:
                    data.cpu_usage_max = cpu_usage.max
                    data.cpu_usage_avg = cpu_usage.avg
                    data.cpu_usage_min = cpu_usage.min

                mem_used_percent = aggs.get("AGT.ECS.mem_usedPercent")
                if mem_used_percent:
                    data.mem_used_percent_max = mem_used_percent.max
                    data.mem_used_percent_avg = mem_used_percent.avg
                    data.mem_used_percent_min = mem_used_percent.min

                has_basic_metric = any([cpu_util, mem_util, disk_util_inband, cpu_usage, mem_used_percent])

                # 磁盘使用率计算
                total_used_max = total_used_avg = total_used_min = 0.0
                total_total_max = total_total_avg = total_total_min = 0.0
                max_percent_max = max_percent_avg = max_percent_min = 0.0
                has_disk_data = False
                has_disk_percent_data = False
                has_used_max = has_used_avg = has_used_min = False
                has_total_max = has_total_avg = has_total_min = False

                for key, agg in aggs.items():
                    if not key.startswith("disk_"):
                        continue
                    for partition in agg.partitions.values():
                        has_disk_data = True
                        if partition.used_max is not None:
                            total_used_max += partition.used_max
                            has_used_max = True
                        if partition.used_avg is not None:
                            total_used_avg += partition.used_avg
                            has_used_avg = True
                        if partition.used_min is not None:
                            total_used_min += partition.used_min
                            has_used_min = True
                        if partition.total_max is not None:
                            total_total_max += partition.total_max
                            has_total_max = True
                        if partition.total_avg is not None:
                            total_total_avg += partition.total_avg
                            has_total_avg = True
                        if partition.total_min is not None:
                            total_total_min += partition.total_min
                            has_total_min = True
                        if partition.used_percent_max is not None:
                            has_disk_percent_data = True
                            if partition.used_percent_max > max_percent_max:
                                max_percent_max = partition.used_percent_max
                        if partition.used_percent_avg is not None:
                            has_disk_percent_data = True
                            if partition.used_percent_avg > max_percent_avg:
                                max_percent_avg = partition.used_percent_avg
                        if partition.used_percent_min is not None:
                            has_disk_percent_data = True
                            if partition.used_percent_min > max_percent_min:
                                max_percent_min = partition.used_percent_min

                if has_disk_data:
                    # max
                    if has_used_max and has_total_max and total_total_max > 0:
                        calc_max = round(total_used_max / total_total_max * 100, 2)
                        if calc_max > 0:
                            data.disk_used_percent_max = calc_max
                        elif has_disk_percent_data and max_percent_max > 0:
                            data.disk_used_percent_max = round(max_percent_max, 2)
                        else:
                            data.disk_used_percent_max = calc_max
                    elif has_disk_percent_data and max_percent_max > 0:
                        data.disk_used_percent_max = round(max_percent_max, 2)

                    # avg
                    if has_used_avg and has_total_avg and total_total_avg > 0:
                        calc_avg = round(total_used_avg / total_total_avg * 100, 2)
                        if calc_avg > 0:
                            data.disk_used_percent_avg = calc_avg
                        elif has_disk_percent_data and max_percent_avg > 0:
                            data.disk_used_percent_avg = round(max_percent_avg, 2)
                        else:
                            data.disk_used_percent_avg = calc_avg
                    elif has_disk_percent_data and max_percent_avg > 0:
                        data.disk_used_percent_avg = round(max_percent_avg, 2)

                    # min
                    if has_used_min and has_total_min and total_total_min > 0:
                        calc_min = round(total_used_min / total_total_min * 100, 2)
                        if calc_min > 0:
                            data.disk_used_percent_min = calc_min
                        elif has_disk_percent_data and max_percent_min > 0:
                            data.disk_used_percent_min = round(max_percent_min, 2)
                        else:
                            data.disk_used_percent_min = calc_min
                    elif has_disk_percent_data and max_percent_min > 0:
                        data.disk_used_percent_min = round(max_percent_min, 2)

                if has_basic_metric:
                    result.append(data)

        return result

    def _upsert_metric_data(self, data_list: list):
        for data in data_list:
            existing = self.db.query(CesMetricData).filter_by(
                instance_id=data.instance_id, timestamp=data.timestamp
            ).first()
            if existing:
                self._merge_metric_data(existing, data)
            else:
                self.db.add(data)
        self.db.commit()

    def _merge_metric_data(self, target: CesMetricData, source: CesMetricData):
        for col in CesMetricData.__table__.columns:
            if col.name in ("instance_id", "timestamp"):
                continue
            new_val = getattr(source, col.name)
            if new_val is None:
                continue
            old_val = getattr(target, col.name)
            if old_val is not None and old_val != 0 and new_val == 0:
                continue
            setattr(target, col.name, new_val)

    # ==================== 日数据聚合 ====================

    def aggregate_to_daily(self, day_start: str = None, day_end: str = None):
        if day_start is None:
            yesterday = datetime.now() - timedelta(days=1)
            day_start = yesterday.strftime("%Y-%m-%d 00:00:00")
            day_end_dt = yesterday + timedelta(days=1)
            day_end = day_end_dt.strftime("%Y-%m-%d 00:00:00")

        all_data = self.db.query(CesMetricData).filter(
            CesMetricData.timestamp >= day_start,
            CesMetricData.timestamp <= day_end
        ).all()

        grouped = OrderedDict()
        for data in all_data:
            grouped.setdefault(data.instance_id, []).append(data)

        day_list = []
        for instance_id, records in grouped.items():
            day_data = self.db.query(CesMetricDataDay).filter_by(
                instance_id=instance_id, timestamp=day_start
            ).first()
            if not day_data:
                day_data = CesMetricDataDay()
                day_data.instance_id = instance_id
                day_data.timestamp = day_start
            day_data.endpoint = records[0].endpoint
            day_data.instance_name = records[0].instance_name

            # max: 取 ces_metric_data 中该云主机当天所有记录的最大值
            val = self._calc_max(records, lambda r: r.cpu_util_max)
            if val is not None: day_data.cpu_util_max = val
            # avg: 取 ces_metric_data 中该云主机当天所有记录的平均值
            val = self._calc_avg(records, lambda r: r.cpu_util_avg)
            if val is not None: day_data.cpu_util_avg = val
            # min: 取 ces_metric_data 中该云主机当天所有记录的最小值
            val = self._calc_min(records, lambda r: r.cpu_util_min)
            if val is not None: day_data.cpu_util_min = val

            val = self._calc_max(records, lambda r: r.mem_util_max)
            if val is not None: day_data.mem_util_max = val
            val = self._calc_avg(records, lambda r: r.mem_util_avg)
            if val is not None: day_data.mem_util_avg = val
            val = self._calc_min(records, lambda r: r.mem_util_min)
            if val is not None: day_data.mem_util_min = val

            val = self._calc_max(records, lambda r: r.disk_util_inband_max)
            if val is not None: day_data.disk_util_inband_max = val
            val = self._calc_avg(records, lambda r: r.disk_util_inband_avg)
            if val is not None: day_data.disk_util_inband_avg = val
            val = self._calc_min(records, lambda r: r.disk_util_inband_min)
            if val is not None: day_data.disk_util_inband_min = val

            val = self._calc_max(records, lambda r: r.cpu_usage_max)
            if val is not None: day_data.cpu_usage_max = val
            val = self._calc_avg(records, lambda r: r.cpu_usage_avg)
            if val is not None: day_data.cpu_usage_avg = val
            val = self._calc_min(records, lambda r: r.cpu_usage_min)
            if val is not None: day_data.cpu_usage_min = val

            val = self._calc_max(records, lambda r: r.mem_used_percent_max)
            if val is not None: day_data.mem_used_percent_max = val
            val = self._calc_avg(records, lambda r: r.mem_used_percent_avg)
            if val is not None: day_data.mem_used_percent_avg = val
            val = self._calc_min(records, lambda r: r.mem_used_percent_min)
            if val is not None: day_data.mem_used_percent_min = val

            val = self._calc_max(records, lambda r: r.disk_used_percent_max)
            if val is not None: day_data.disk_used_percent_max = val
            val = self._calc_avg(records, lambda r: r.disk_used_percent_avg)
            if val is not None: day_data.disk_used_percent_avg = val
            val = self._calc_min(records, lambda r: r.disk_used_percent_min)
            if val is not None: day_data.disk_used_percent_min = val

            day_list.append(day_data)

        if day_list:
            for day_data in day_list:
                existing = self.db.query(CesMetricDataDay).filter_by(
                    instance_id=day_data.instance_id, timestamp=day_data.timestamp
                ).first()
                if existing:
                    for col in CesMetricDataDay.__table__.columns:
                        if col.name in ("instance_id", "timestamp"):
                            continue
                        new_val = getattr(day_data, col.name)
                        if new_val is not None:
                            setattr(existing, col.name, new_val)
                else:
                    self.db.add(day_data)
            self.db.commit()
            logger.info("聚合 %d 台云主机的日数据完成，时间=%s", len(day_list), day_start)

    def _calc_max(self, records: list, extractor) -> float:
        values = [extractor(r) for r in records]
        values = [v for v in values if v is not None and v != 0]
        return max(values) if values else None

    def _calc_avg(self, records: list, extractor) -> float:
        values = [extractor(r) for r in records]
        values = [v for v in values if v is not None and v != 0]
        return sum(values) / len(values) if values else None

    def _calc_min(self, records: list, extractor) -> float:
        values = [extractor(r) for r in records]
        values = [v for v in values if v is not None and v != 0]
        return min(values) if values else None

    # ==================== 指标 Upsert ====================

    def _upsert_metrics(self, metrics: list):
        for metric in metrics:
            existing = self.db.query(CesMetric).filter_by(
                namespace=metric.namespace,
                metric_name=metric.metric_name,
                dimension_name=metric.dimension_name,
                dimension_value=metric.dimension_value,
            ).first()
            if existing:
                for col in CesMetric.__table__.columns:
                    if col.name in ("namespace", "metric_name", "dimension_name", "dimension_value"):
                        continue
                    new_val = getattr(metric, col.name)
                    if new_val is not None:
                        setattr(existing, col.name, new_val)
            else:
                self.db.add(metric)
        self.db.commit()
