import * as XLSX from 'xlsx'
import i18n from '@/i18n'

function getLang() {
  return i18n.global.locale.value
}

const departments = ['市卫健委', '市教育局', '市公安局', '市交通局', '市住建局', '市财政局', '市人社局', '市自然资源局', '市生态环境局', '市水务局']
const appSystems = ['基卫云系统', '智慧交通系统', '住房租赁平台', '政务办公系统', '医保管理系统', '教育资源平台', '公共安全系统', '城市管理系统', '应急指挥系统', '数字档案系统']
const statuses = ['运行中', '已关机', '异常']
const osList = ['CentOS 7.6', 'CentOS 8.2', 'Ubuntu 20.04', 'Ubuntu 22.04', 'Windows Server 2019', 'Windows Server 2022', 'Kylin V10', 'UOS V20']
const specs = ['2vCPU 4GB', '4vCPU 8GB', '8vCPU 16GB', '8vCPU 32GB', '16vCPU 32GB', '16vCPU 64GB', '32vCPU 64GB', '32vCPU 128GB']
const architectures = ['x86_64', 'ARM64']
const regions = ['华东-上海一', '华东-上海二', '华北-北京一', '华北-北京四', '华南-广州', '西南-贵阳一']

function randomItem(arr) {
  return arr[Math.floor(Math.random() * arr.length)]
}

function randomIP() {
  return `192.168.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 254) + 1}`
}

const cpuOptions = [2, 4, 8, 16, 32]
const memoryOptions = [4, 8, 16, 32, 64, 128]

function generateMockList(total = 86) {
  const list = []
  for (let i = 0; i < total; i++) {
    const cpu = randomItem(cpuOptions)
    const memory = randomItem(memoryOptions)
    const systemDisk = randomItem([40, 50, 80, 100, 200])
    const dataDisk = randomItem([0, 50, 100, 200, 500, 1000])
    // 委办局和应用系统先确定，主机名称从中派生，保持一致
    const department = randomItem(departments)
    const appSystem = randomItem(appSystems)
    const deptShort = department.slice(1) // 去掉"市"字
    const appShort = appSystem.slice(0, 4)
    list.push({
      id: `vm-${String(i + 1).padStart(4, '0')}`,
      hostName: `${deptShort}_${appShort}_主机${String(i + 1).padStart(3, '0')}`,
      department,
      appSystem,
      ipAddress: randomIP(),
      status: randomItem(statuses),
      os: randomItem(osList),
      spec: randomItem(specs),
      architecture: randomItem(architectures),
      region: randomItem(regions),
      cpu,
      memory,
      systemDisk,
      dataDisk
    })
  }
  return list
}

const allMockData = generateMockList(86)

export function getMockList(params) {
  const { department, appSystem, hostName, ipAddress, status, cpu, memory, systemDiskMin, systemDiskMax, dataDiskMin, dataDiskMax, pageNum = 1, pageSize = 10 } = params

  let filtered = [...allMockData]

  if (department) {
    filtered = filtered.filter(item => item.department.includes(department))
  }
  if (appSystem) {
    filtered = filtered.filter(item => item.appSystem.includes(appSystem))
  }
  if (hostName) {
    filtered = filtered.filter(item => item.hostName.includes(hostName))
  }
  if (ipAddress) {
    filtered = filtered.filter(item => item.ipAddress.includes(ipAddress))
  }
  if (status) {
    filtered = filtered.filter(item => item.status === status)
  }
  if (cpu !== undefined && cpu !== null && cpu !== '') {
    filtered = filtered.filter(item => item.cpu === Number(cpu))
  }
  if (memory !== undefined && memory !== null && memory !== '') {
    filtered = filtered.filter(item => item.memory === Number(memory))
  }
  if (systemDiskMin !== undefined && systemDiskMin !== null && systemDiskMin !== '') {
    filtered = filtered.filter(item => item.systemDisk >= Number(systemDiskMin))
  }
  if (systemDiskMax !== undefined && systemDiskMax !== null && systemDiskMax !== '') {
    filtered = filtered.filter(item => item.systemDisk <= Number(systemDiskMax))
  }
  if (dataDiskMin !== undefined && dataDiskMin !== null && dataDiskMin !== '') {
    filtered = filtered.filter(item => item.dataDisk >= Number(dataDiskMin))
  }
  if (dataDiskMax !== undefined && dataDiskMax !== null && dataDiskMax !== '') {
    filtered = filtered.filter(item => item.dataDisk <= Number(dataDiskMax))
  }

  const total = filtered.length
  const start = (pageNum - 1) * pageSize
  const end = start + pageSize
  const list = filtered.slice(start, end)

  return {
    code: 200,
    data: {
      list,
      total,
      pageNum,
      pageSize
    }
  }
}

export function getMockFilterOptions() {
  const cpuSet = new Set(allMockData.map(item => item.cpu))
  const memorySet = new Set(allMockData.map(item => item.memory))
  const statusSet = new Set(allMockData.map(item => item.status))
  return {
    cpuOptions: [...cpuSet].sort((a, b) => a - b),
    memoryOptions: [...memorySet].sort((a, b) => a - b),
    statusOptions: [...statusSet].sort()
  }
}

export function mockExportReport(params) {
  console.log('导出报告参数:', params)
  return { code: 200, message: '导出成功' }
}

// ==================== 前端 Mock 数据导出 Excel ====================

/**
 * 使用前端 mock 列表数据生成 Excel 并下载
 * @param {Array} list - 当前页面的云主机列表数据
 * @param {string} startDate
 * @param {string} endDate
 */
export function exportMockListExcel(list, startDate, endDate) {
  const lang = getLang()
  const headers = lang === 'en' ? [
    'ECS ID', 'ECS Name', 'Created At', 'Status',
    'Department', 'App System', 'Region', 'Network Zone',
    'OS', 'Flavor', 'CPU Arch',
    'CPU (cores)', 'Memory (GB)', 'System Disk (GB)', 'Data Disk (GB)',
    'IP Address',
    'CPU Util Max (%)', 'CPU Util Avg (%)', 'CPU Util Min (%)',
    'Mem Util Max (%)', 'Mem Util Avg (%)', 'Mem Util Min (%)',
    'Disk Util Max (%)', 'Disk Util Avg (%)', 'Disk Util Min (%)',
  ] : [
    '云主机ID', '主机名称', '创建时间', '运行状态',
    '委办局', '应用系统', '区域', '网络分区',
    '操作系统', '规格', 'CPU架构',
    'CPU(核)', '内存(GB)', '系统盘(GB)', '数据盘(GB)',
    'IP地址',
    'CPU使用率峰值(%)', 'CPU使用率均值(%)', 'CPU使用率最小值(%)',
    '内存使用率峰值(%)', '内存使用率均值(%)', '内存使用率最小值(%)',
    '磁盘使用率峰值(%)', '磁盘使用率均值(%)', '磁盘使用率最小值(%)',
  ]
  const rows = (list || []).map(item => {
    const cpuBase = 15 + Math.random() * 50
    const memBase = 30 + Math.random() * 40
    const diskBase = 20 + Math.random() * 35
    return [
      item.id || '', item.hostName || '', '', item.status || '',
      item.department || '', item.appSystem || '', item.region || '', '',
      item.os || '', item.spec || '', item.architecture || '',
      item.cpu || '', item.memory || '', item.systemDisk || '', item.dataDisk || '',
      item.ipAddress || '',
      Math.round((cpuBase + Math.random() * 25) * 100) / 100,
      Math.round(cpuBase * 100) / 100,
      Math.round(Math.max(0, cpuBase - Math.random() * 15) * 100) / 100,
      Math.round((memBase + Math.random() * 20) * 100) / 100,
      Math.round(memBase * 100) / 100,
      Math.round(Math.max(0, memBase - Math.random() * 10) * 100) / 100,
      Math.round((diskBase + Math.random() * 15) * 100) / 100,
      Math.round(diskBase * 100) / 100,
      Math.round(Math.max(0, diskBase - Math.random() * 10) * 100) / 100,
    ]
  })
  const wsData = [headers, ...rows]
  const ws = XLSX.utils.aoa_to_sheet(wsData)
  ws['!cols'] = headers.map(() => ({ wch: 18 }))
  const wb = XLSX.utils.book_new()
  const sheetName = lang === 'en' ? 'ECS Report' : '弹性云服务器报告'
  XLSX.utils.book_append_sheet(wb, ws, sheetName)
  const filePrefix = lang === 'en' ? 'ECS_Report' : '弹性云服务器报告'
  const fileName = `${filePrefix}_${startDate}_${endDate}.xlsx`
  XLSX.writeFile(wb, fileName)
  return { code: 200 }
}

/**
 * 使用前端 mock 监控数据生成 Excel 并下载
 * @param {string} hostName - 主机名称
 * @param {Array} metricData - 监控数据点数组
 * @param {string} startDate
 * @param {string} endDate
 */
export function exportMockMetricExcel(hostName, metricData, startDate, endDate) {
  const lang = getLang()
  const headers = lang === 'en' ? [
    'Timestamp', 'CPU Util Max (%)', 'CPU Util Avg (%)', 'CPU Util Min (%)',
    'Mem Util Max (%)', 'Mem Util Avg (%)', 'Mem Util Min (%)',
    'Disk Util Max (%)', 'Disk Util Avg (%)', 'Disk Util Min (%)'
  ] : [
    '时间', 'CPU使用率峰值(%)', 'CPU使用率均值(%)', 'CPU使用率最小值(%)',
    '内存使用率峰值(%)', '内存使用率均值(%)', '内存使用率最小值(%)',
    '磁盘使用率峰值(%)', '磁盘使用率均值(%)', '磁盘使用率最小值(%)'
  ]
  const rows = (metricData || []).map(d => [
    d.timestamp || '',
    d.cpuUtilMax ?? '', d.cpuUtilAvg ?? '', d.cpuUtilMin ?? '',
    d.memUtilMax ?? '', d.memUtilAvg ?? '', d.memUtilMin ?? '',
    d.diskUtilMax ?? '', d.diskUtilAvg ?? '', d.diskUtilMin ?? ''
  ])
  const wsData = [headers, ...rows]
  const ws = XLSX.utils.aoa_to_sheet(wsData)
  ws['!cols'] = headers.map(() => ({ wch: 22 }))
  const wb = XLSX.utils.book_new()
  const sheetName = lang === 'en' ? 'Metric Data' : '监控数据'
  XLSX.utils.book_append_sheet(wb, ws, sheetName)
  const name = hostName || (lang === 'en' ? 'Host' : '主机')
  const metricName = lang === 'en' ? 'Metric_Data' : '监控数据'
  const fileName = `${name}_${metricName}_${startDate}_${endDate}.xlsx`
  XLSX.writeFile(wb, fileName)
  return { code: 200 }
}

// ==================== 主机详情 Mock ====================

export function getMockDetail(serverId) {
  const lang = getLang()
  const item = allMockData.find(d => d.id === serverId) || allMockData[0]
  const sysDiskLabel = lang === 'en' ? 'System Disk' : '系统盘'
  const dataDiskLabel = lang === 'en' ? 'Data Disk' : '数据盘'
  const ultraIOLabel = lang === 'en' ? 'Ultra High IO' : '超高IO'
  const highIOLabel = lang === 'en' ? 'High IO' : '高IO'
  return {
    code: 200,
    data: {
      id: item.id,
      hostName: item.hostName,
      department: item.department,
      appSystem: item.appSystem,
      ipAddress: item.ipAddress,
      ipv6: '',
      publicEip: '',
      status: item.status,
      os: item.os,
      osName: item.os,
      spec: item.spec,
      architecture: item.architecture,
      region: item.region,
      availabilityZone: item.region + (lang === 'en' ? '-AZ1' : '-可用区1'),
      cpu: item.cpu,
      memory: item.memory,
      systemDisk: item.systemDisk,
      dataDisk: item.dataDisk,
      createdAt: '2024-01-15T10:30:00',
      imageName: item.os + (lang === 'en' ? ' Image' : ' 镜像'),
      projectId: 'mock-project-001',
      regionName: item.region,
      networkZone: lang === 'en' ? 'Internet Zone' : '互联网区',
      volumes: [
        { volumeId: `vol-sys-${item.id}`, name: sysDiskLabel, size: item.systemDisk, volumeType: 'SSD', ioLabel: ultraIOLabel, bootable: true, diskType: sysDiskLabel },
        ...(item.dataDisk > 0 ? [{ volumeId: `vol-data-${item.id}`, name: dataDiskLabel, size: item.dataDisk, volumeType: 'SAS', ioLabel: highIOLabel, bootable: false, diskType: dataDiskLabel }] : [])
      ]
    }
  }
}

// ==================== 监控数据 Mock ====================

export function getMockMetricData(serverId, params) {
  const { startDate, endDate, period } = params
  const points = []
  const start = new Date(startDate)
  const end = new Date(endDate)
  const diffHours = Math.max(1, (end - start) / (1000 * 60 * 60))

  if (period === 'day') {
    const days = Math.max(1, Math.ceil(diffHours / 24))
    for (let i = 0; i < days; i++) {
      const d = new Date(start.getTime() + i * 24 * 60 * 60 * 1000)
      const dateStr = d.toISOString().slice(0, 10) + ' 00:00:00.000000'
      const base = 20 + Math.random() * 40
      points.push({
        timestamp: dateStr,
        cpuUtilMax: Math.round((base + Math.random() * 30) * 100) / 100,
        cpuUtilAvg: Math.round(base * 100) / 100,
        cpuUtilMin: Math.round((base - Math.random() * 15) * 100) / 100,
        memUtilMax: Math.round((base + 10 + Math.random() * 20) * 100) / 100,
        memUtilAvg: Math.round((base + 10) * 100) / 100,
        memUtilMin: Math.round((base + 10 - Math.random() * 10) * 100) / 100,
        diskUtilMax: Math.round((base - 5 + Math.random() * 15) * 100) / 100,
        diskUtilAvg: Math.round((base - 5) * 100) / 100,
        diskUtilMin: Math.round((base - 5 - Math.random() * 10) * 100) / 100,
      })
    }
  } else {
    // 5min interval
    const count = Math.min(Math.ceil(diffHours * 12), 288)
    for (let i = 0; i < count; i++) {
      const d = new Date(start.getTime() + i * 5 * 60 * 1000)
      const dateStr = d.toISOString().slice(0, 19).replace('T', ' ') + '.000000'
      const base = 20 + Math.random() * 40
      points.push({
        timestamp: dateStr,
        cpuUtilMax: Math.round((base + Math.random() * 30) * 100) / 100,
        cpuUtilAvg: Math.round(base * 100) / 100,
        cpuUtilMin: Math.round((base - Math.random() * 15) * 100) / 100,
        memUtilMax: Math.round((base + 10 + Math.random() * 20) * 100) / 100,
        memUtilAvg: Math.round((base + 10) * 100) / 100,
        memUtilMin: Math.round((base + 10 - Math.random() * 10) * 100) / 100,
        diskUtilMax: Math.round((base - 5 + Math.random() * 15) * 100) / 100,
        diskUtilAvg: Math.round((base - 5) * 100) / 100,
        diskUtilMin: Math.round((base - 5 - Math.random() * 10) * 100) / 100,
      })
    }
  }

  return { code: 200, data: points }
}
