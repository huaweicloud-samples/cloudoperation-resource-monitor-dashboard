# cloudoperation-resource-monitor-dashboard

> Huawei Cloud Resource Monitor Dashboard — A platform for collecting, displaying, and exporting ECS, EVS, and CES monitoring data

[中文文档](README_zh.md)

[![Status](https://img.shields.io/badge/Status-Incubating-blue)]()
[![Huawei Cloud](https://img.shields.io/badge/Huawei%20Cloud-Samples-red)]()
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?logo=fastapi)
![Vue](https://img.shields.io/badge/Vue-3.4+-4FC08D?logo=vue.js)
![Element Plus](https://img.shields.io/badge/Element_Plus-2.9+-409EFF?logo=element)
![SQLite](https://img.shields.io/badge/SQLite-✓-003B57?logo=sqlite)

---

## Overview

HuaweiCloud Resource Monitor Dashboard is a resource monitoring dashboard for **Huawei Cloud Elastic Cloud Server (ECS), Elastic Volume Service (EVS), and Cloud Eye Service (CES)**. After configuring tenant AKSK authentication via the frontend, the backend periodically or manually collects resource data and utilization metrics from Huawei Cloud APIs, stores them in a local SQLite database, and provides query, filtering, and report export capabilities through RESTful APIs.

### Core Problems Solved

In multi-project, multi-region Huawei Cloud environments, operations teams typically face the following challenges:

- **Difficult resource inventory**: Cloud servers are scattered across different regions and projects, lacking a unified view
- **Opaque utilization**: CPU, memory, and disk utilization data is dispersed across the Cloud Eye service, making it hard to batch-fetch and compare
- **Tedious report generation**: Regular inspections require manually exporting multiple datasets and assembling reports, which is inefficient
- **Unclear resource ownership**: The mapping between cloud server naming conventions and departments/application systems requires manual maintenance

This platform helps operations teams efficiently complete resource inspections and report output through **scheduled data collection + multi-dimensional filtering + one-click report export**.

---

## Features

- **Authentication Configuration Management**: Manage multi-tenant authentication info (AKSK) via the frontend settings page, with support for adding, editing, and deleting; each tenant can trigger resource refresh independently
- **ECS Cloud Server Data Collection**: Automatically fetch all elastic cloud server information from Huawei Cloud ECS API with pagination, including specifications, OS, IP addresses, etc.
- **EVS Cloud Disk Data Collection**: Automatically fetch cloud disk information, associate with corresponding cloud servers, distinguish system/data disks and disk types (high IO/ultra-high IO)
- **CES Monitoring Metric Collection**: Batch-fetch CPU utilization, memory utilization, disk utilization, and other monitoring data; supports dual-source collection from system metrics (SYS.ECS) and Agent metrics (AGT.ECS)
- **Scheduled Auto-Collection**: Scheduled task execution time and monitoring data granularity are configurable via the Settings page, defaulting to daily at 2:00 AM with 5-minute data granularity
- **Parse Rule Configuration**: Configure cloud server name parsing rules to automatically extract department and application system info from naming conventions
- **Multi-condition Filtering & Query**: Filter by department, application system, host name, IP address, host status, CPU cores, memory size, system/data disk range, etc.
- **Host Detail Page**: Click a cloud server to navigate to the detail page, displaying host basic info, disk info, and utilization monitoring charts with time range and data granularity switching
- **Single Host Monitoring Data Export**: Export utilization data for a single host as an Excel file from the host detail page
- **Excel Report Export**: Select a date range and one-click export an Excel report containing resource info and monitoring utilization
- **Mock Data Auto-Fallback**: When the backend API has no data or requests fail, the frontend automatically uses Mock data for display, ensuring page availability
- **CPU Architecture Auto-Detection**: Automatically determine X86 / ARM / IES architecture based on cloud server specification names
- **Department/Application Auto-Parsing**: Automatically parse ownership info from cloud server naming conventions (`hostname_prefix_{department}_{application}_...`)
- **API Rate-Limit Auto-Retry**: Automatically retry (up to 3 times, 60-second interval) when Huawei Cloud API returns 429 rate-limiting

---

## Screenshots

### Cloud Server List

![Cloud Server List](resources/ecs_list.png)

### Search Results

![Search Results](resources/ecs_search.png)

### Export Report

![Export Report](resources/export.png)

### Authentication Configuration

![Authentication Configuration](resources/config.png)

### Export Report Template

The exported Excel report template can be found at [resources/弹性云服务器报告.xlsx](resources/弹性云服务器报告.xlsx), containing cloud server basic info and CPU/memory/disk utilization data.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                       Frontend (Vue 3)                           │
│  ┌─────────────┐ ┌──────────────┐ ┌────────────┐ ┌───────────┐ │
│  │ CloudVmList  │ │ServerDetail  │ │  Settings   │ │ExportDialog│ │
│  │  (VM List)   │ │(Host Detail) │ │(Parse/Sched/│ │  (Export)  │ │
│  │              │ │              │ │  Auth Cfg)  │ │            │ │
│  └─────────────┘ └──────────────┘ └────────────┘ └───────────┘ │
│       Vue Router + Element Plus + Day.js + Canvas Charts         │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    API Layer (Axios)                         │ │
│  │          Mock Fallback: Auto-use Mock data when unavailable  │ │
│  └────────────────────────────┬────────────────────────────────┘ │
└────────────────────────────────┼─────────────────────────────────┘
                                 │ HTTP
┌────────────────────────────────┼─────────────────────────────────┐
│                    Backend (FastAPI)                              │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │   Routers     │  │   Services   │  │     Scheduler          │  │
│  │ (cloud_vm,   )│  │ (ecs/evs/ces)│  │   (APScheduler)        │  │
│  │  (config)    )│  │              │  │                        │  │
│  └──────┬───────┘  └──────┬───────┘  └───────────────────────┘  │
│         │                 │                                      │
│  ┌──────┴───────┐  ┌──────┴───────┐                             │
│  │   Models      │  │ HwCloudClient│                             │
│  │  (SQLAlchemy) │  │(Sign+Retry)  │                             │
│  └──────┬───────┘  └──────┬───────┘                             │
│         │                 │                                      │
└─────────┼─────────────────┼──────────────────────────────────────┘
          │                 │
    ┌─────┴─────┐    ┌──────┴──────┐
    │  SQLite   │    │Huawei Cloud │
    │ (8 tables)│    │ ECS/EVS/CES │
    └───────────┘    └─────────────┘
```

---

## Project Structure

```
huaweicloud-resource-monitor-dashboard/
├── resources/                        # Screenshots & export templates
│   ├── ecs_list.png                  # Cloud server list screenshot
│   ├── ecs_search.png                # Search results screenshot
│   ├── export.png                    # Export report screenshot
│   ├── config.png                    # Auth config screenshot
│   └── 弹性云服务器报告.xlsx          # Export report template
├── backend/                          # Backend Python project
│   ├── app.py                        # FastAPI application entry
│   ├── config.py                     # Configuration (port, DB, scheduler, CPU arch specs)
│   ├── database.py                   # Database init & connection management
│   ├── models.py                     # SQLAlchemy ORM models (8 tables)
│   ├── schemas.py                    # Pydantic request/response models
│   ├── scheduler.py                  # APScheduler scheduled task dispatch
│   ├── init_data.py                  # Initial data collection on startup
│   ├── requirements.txt              # Python dependencies
│   ├── routers/
│   │   ├── cloud_vm.py               # Cloud server API routes (list, detail, metrics, export)
│   │   └── config.py                 # Auth config API routes (CRUD, per-tenant refresh)
│   └── services/
│       ├── hwcloud_client.py         # Huawei Cloud API signing & HTTP client
│       ├── ecs_service.py            # ECS cloud server data collection service
│       ├── evs_service.py            # EVS cloud disk data collection service
│       └── ces_service.py            # CES monitoring metric data collection service
└── frontend/                         # Frontend Vue3 project
    ├── index.html                    # HTML entry
    ├── package.json                  # Frontend dependency config
    ├── vite.config.js                # Vite build config
    ├── src/
    │   ├── main.js                   # Vue application entry
    │   ├── App.vue                   # Root component (navbar + Router View)
    │   ├── router/
    │   │   └── index.js              # Vue Router config
    │   ├── api/
    │   │   └── cloudVm.js            # API request wrapper (with Mock Fallback)
    │   ├── config/
    │   │   └── api.js                # API path config
    │   ├── mock/
    │   │   └── cloudVm.js            # Mock data (list, detail, metrics)
    │   ├── components/
    │   │   └── ExportDialog.vue      # Export report dialog component
    │   └── views/
    │       ├── CloudVmList.vue       # Cloud server list page (main page)
    │       ├── ServerDetail.vue      # Host detail page (info + monitoring charts)
    │       └── Settings.vue          # System settings page (parse rules, scheduler, auth)
    └── dist/                         # Build output
```

---

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm 9+

### 1. Start the Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

The backend service will start at `http://localhost:8080` and automatically perform a full data collection on startup.

### 2. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend dev server will start at `http://localhost:3000`, with API requests automatically proxied to the backend at `localhost:8080`.

### 3. Configure Authentication

Open `http://localhost:3000` in your browser, navigate to the **Settings** page (click the gear icon in the header). The Settings page has three tabs:

1. **Parse Rules** — Configure cloud server name parsing rules to auto-extract department and application system info
2. **Scheduled Task** — Configure execution time and monitoring data granularity
3. **Auth Config** — Add Huawei Cloud tenant authentication info

| Field | Description |
|-------|-------------|
| Region Name | Huawei Cloud region, e.g. `cn-north-4` |
| API Endpoint | Region API endpoint, e.g. `cn-north-4.myhuaweicloud.com` |
| Project ID | Huawei Cloud project ID |
| Access Key | IAM user AK |
| Secret Key | IAM user SK |
| Network Zone | Network zone identifier, e.g. `Huawei Public Cloud` |

After adding, click the **Refresh Resources** button to trigger resource data collection for that tenant.

> On first use, if the backend database has no data yet, the frontend will automatically display pages using Mock data.

---

## Production Deployment

### Frontend Build

```bash
cd frontend
npm run build
```

The build output is in the `frontend/dist/` directory and can be deployed to Nginx or other static file servers. Example Nginx config:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /path/to/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Backend Deployment

```bash
cd backend
pip install -r requirements.txt
# Run directly
python app.py

# Or use Gunicorn + Uvicorn Workers
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8080
```

---

## API Reference

### Cloud Server APIs

All endpoints are prefixed with `/api/cloud-vm`.

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/cloud-vm/list` | Paginated query for cloud server list |
| GET | `/api/cloud-vm/detail/{server_id}` | Get cloud server details (including disk info) |
| GET | `/api/cloud-vm/metric-data/{server_id}` | Get monitoring data for a single host |
| GET | `/api/cloud-vm/export-metric/{server_id}` | Export single host monitoring data as Excel |
| POST | `/api/cloud-vm/export` | Export Excel monitoring report |
| GET | `/api/cloud-vm/fetch-metric-data` | Manually trigger monitoring data collection |
| GET | `/hello` | Health check |

### Authentication Config APIs

All endpoints are prefixed with `/api/config`.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/config/list` | Get all authentication configs |
| POST | `/api/config/add` | Add authentication config |
| PUT | `/api/config/update` | Update authentication config (AK/SK/Network Zone) |
| DELETE | `/api/config/delete` | Delete authentication config |
| POST | `/api/config/refresh` | Trigger resource refresh per tenant (async) |

### Parse Rule APIs

All endpoints are prefixed with `/api/config`.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/config/parse-rules` | Get all parse rules |
| POST | `/api/config/parse-rules/add` | Add parse rule |
| PUT | `/api/config/parse-rules/update` | Update parse rule |
| DELETE | `/api/config/parse-rules/delete` | Delete parse rule |

### Scheduler Config APIs

All endpoints are prefixed with `/api/config`.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/config/scheduler` | Get scheduler config (cron expression + metric period) |
| PUT | `/api/config/scheduler/update` | Update scheduler config |

### Request Parameters

**POST `/api/cloud-vm/list`**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| department | string | No | Department (fuzzy match) |
| appSystem | string | No | Application system (fuzzy match) |
| hostName | string | No | Host name (fuzzy match) |
| ipAddress | string | No | IP address (fuzzy match) |
| status | string | No | Host status (exact match, e.g. `Running`, `Stopped`, `Error`) |
| cpu | string | No | CPU cores (exact match) |
| memory | string | No | Memory size in GB (exact match) |
| systemDiskMin | int | No | System disk minimum in GB |
| systemDiskMax | int | No | System disk maximum in GB |
| dataDiskMin | int | No | Data disk minimum in GB |
| dataDiskMax | int | No | Data disk maximum in GB |
| pageNum | int | No | Page number, default 1 |
| pageSize | int | No | Page size, default 10 |

**GET `/api/cloud-vm/detail/{server_id}`**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| server_id | string | Yes | Cloud server ID (path parameter) |

**GET `/api/cloud-vm/metric-data/{server_id}`**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| server_id | string | Yes | Cloud server ID (path parameter) |
| startDate | string | Yes | Start date, format `YYYY-MM-DD` |
| endDate | string | Yes | End date, format `YYYY-MM-DD` |
| period | string | No | Data granularity, `5min` (default) or `day` |

**POST `/api/cloud-vm/export`**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| startDate | string | Yes | Start date, format `YYYY-MM-DD` |
| endDate | string | Yes | End date, format `YYYY-MM-DD` |
| Other filter params | - | No | Same as `/list` endpoint |

**POST `/api/config/add`**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| regionName | string | Yes | Region name |
| endpoint | string | Yes | API endpoint |
| projectId | string | Yes | Project ID |
| ak | string | Yes | Access Key |
| sk | string | Yes | Secret Key |
| networkZone | string | No | Network zone |

**POST `/api/config/refresh`**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| regionName | string | Yes | Region name |
| endpoint | string | Yes | API endpoint |
| projectId | string | Yes | Project ID |

---

## Database Model

The project uses an SQLite database with the following 8 tables:

| Table | Description | Primary Key |
|-------|-------------|-------------|
| `ecs_config` | ECS authentication config | (region_name, endpoint, project_id) |
| `ecs_server` | Elastic cloud servers | server_id |
| `evs_volume` | Cloud disks | volume_id |
| `ces_metric` | CES monitoring metrics | (namespace, metric_name, dimension_name, dimension_value) |
| `ces_metric_data` | Monitoring sample data | (instance_id, timestamp) |
| `ces_metric_data_day` | Monitoring daily aggregated data | (instance_id, timestamp) |
| `parse_rule` | Cloud server name parse rules | id |
| `scheduler_config` | Scheduled task and data granularity config | id |

### Monitoring Metric Fields

The `ces_metric_data` and `ces_metric_data_day` tables contain the following monitoring metrics (each group includes max/avg/min statistics):

| Field Prefix | Description | Data Source |
|--------------|-------------|-------------|
| `cpu_util` | CPU utilization | SYS.ECS (system metrics) |
| `mem_util` | Memory utilization | SYS.ECS (system metrics) |
| `disk_util_inband` | Disk utilization (in-band) | SYS.ECS (system metrics) |
| `cpu_usage` | CPU usage | AGT.ECS (Agent metrics) |
| `mem_used_percent` | Memory usage percentage | AGT.ECS (Agent metrics) |
| `disk_used_percent` | Disk usage percentage | AGT.ECS (Agent metrics) |

System metrics (SYS.ECS) are preferred when querying; Agent metrics (AGT.ECS) serve as fallback.

---

## Configuration

All configuration items support environment variable overrides:

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `HWCloud_DB_PATH` | `hwcloud_resource_monitor.db` | SQLite database file path |
| `HWCloud_SERVER_PORT` | `8080` | Backend service listen port |
| `HWCloud_CPU_ARCH_X86_SPECS` | (preset spec list) | X86 architecture spec name set |
| `HWCloud_CPU_ARCH_AARCH64_SPECS` | (preset spec list) | ARM architecture spec name set |
| `HWCloud_CPU_ARCH_IES_SPECS` | (preset spec list) | IES architecture spec name set |

---

## Scheduled Tasks

The system uses APScheduler for scheduled data collection. By default, it runs daily at 2:00 AM with 5-minute monitoring data granularity. Both the execution time and data granularity can be configured via the **Settings > Scheduled Task** page.

Scheduled task execution flow:

1. Collect ECS cloud server data
2. Collect EVS cloud disk data
3. Collect CES metric list
4. Collect previous day's CES monitoring sample data (using configured data granularity)
5. Aggregate previous day's monitoring daily data

### Data Granularity Options

| Period | Description |
|--------|-------------|
| 1 minute | 60-second sampling interval |
| 5 minutes | 300-second sampling interval (default) |
| 20 minutes | 1200-second sampling interval |
| 1 hour | 3600-second sampling interval |
| 4 hours | 14400-second sampling interval |
| 1 day | 86400-second sampling interval |

> For details on data granularity, see [Huawei Cloud CES API Documentation](https://support.huaweicloud.com/api-ces/ces_03_0034.html#section5)

---

## Tech Stack

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| FastAPI | >=0.104.0 | Web framework |
| Uvicorn | >=0.24.0 | ASGI server |
| SQLAlchemy | >=2.0.0 | ORM |
| APScheduler | >=3.10.0 | Scheduled task dispatch |
| Requests | >=2.31.0 | HTTP client (Huawei Cloud API calls) |
| OpenPyXL | >=3.1.0 | Excel file generation |
| Pydantic | >=2.0.0 | Data validation |
| Python-Dotenv | >=1.0.0 | Environment variable loading |

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| Vue 3 | ^3.4.0 | Frontend framework (Composition API) |
| Vue Router | ^4.0.0 | Frontend routing |
| Element Plus | ^2.9.0 | UI component library |
| Axios | ^1.7.0 | HTTP requests |
| Day.js | ^1.11.0 | Date handling |
| Vite | ^5.4.0 | Build tool |

---

## Contributing

Please use pull requests and follow the repository review rules.

## License

This project is licensed under the MIT-0 license.

## Maintainers

CODEOWNERS: @Ferguson2211

## Feedback

Please use GitHub Issues: https://github.com/huaweicloud-samples/cloudoperation-resource-monitor-dashboard/issues
