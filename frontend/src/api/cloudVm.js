import axios from 'axios'
import * as XLSX from 'xlsx'
import { API_BASE_URL, API_PATHS } from '@/config/api'
import { getMockList, getMockDetail, getMockMetricData, exportMockListExcel, exportMockMetricExcel } from '@/mock/cloudVm'

const request = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000
})

request.interceptors.response.use(
  response => response.data,
  error => Promise.reject(error)
)

/**
 * 解析后端返回的 Excel blob，检查数据行数
 * 如果只有表头（1行），则使用 fallback 数据导出
 * 否则直接下载后端返回的 Excel
 */
async function checkExcelAndDownload(response, fallbackData, fallbackStartDate, fallbackEndDate, type) {
  try {
    const arrayBuffer = await response.data.arrayBuffer()
    const data = new Uint8Array(arrayBuffer)
    const workbook = XLSX.read(data, { type: 'array' })
    const sheetName = workbook.SheetNames[0]
    const sheet = workbook.Sheets[sheetName]
    const jsonData = XLSX.utils.sheet_to_json(sheet, { header: 1 })
    // jsonData[0] 是表头，jsonData.length <= 1 说明只有表头没有数据
    if (jsonData.length <= 1) {
      console.log('[Mock Fallback] 后端导出 Excel 无数据行，使用页面数据导出')
      return doFallbackExport(fallbackData, fallbackStartDate, fallbackEndDate, type)
    }
    // 有数据，直接下载后端返回的 Excel
    downloadArrayBuffer(arrayBuffer, response.headers)
    return { code: 200 }
  } catch (err) {
    console.log('[Mock Fallback] 解析 Excel 失败，使用页面数据导出', err)
    return doFallbackExport(fallbackData, fallbackStartDate, fallbackEndDate, type)
  }
}

function doFallbackExport(fallbackData, fallbackStartDate, fallbackEndDate, type) {
  if (type === 'list' && fallbackData && fallbackData.length > 0) {
    return exportMockListExcel(fallbackData, fallbackStartDate, fallbackEndDate)
  } else if (type === 'metric' && fallbackData && fallbackData.metricData && fallbackData.metricData.length > 0) {
    return exportMockMetricExcel(fallbackData.hostName, fallbackData.metricData, fallbackData.startDate, fallbackData.endDate)
  }
  return { code: 500, message: '无数据可导出' }
}

function downloadArrayBuffer(arrayBuffer, headers) {
  const blob = new Blob([arrayBuffer], {
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  const contentDisposition = headers && headers['content-disposition']
  let fileName = '监控数据.xlsx'
  if (contentDisposition) {
    const match = contentDisposition.match(/filename\*?=(?:UTF-8'')?(.+)/i)
    if (match) {
      fileName = decodeURIComponent(match[1].replace(/"/g, ''))
    }
  }
  link.download = fileName
  link.click()
  window.URL.revokeObjectURL(url)
}

// ==================== 云主机列表 ====================

export function fetchCloudVmList(params) {
  return request.post(API_PATHS.CLOUD_VM_LIST, params).then(res => {
    // 后端返回非200或数据为空，使用 mock
    if (res.code !== 200 || !res.data || !res.data.list || res.data.list.length === 0) {
      console.log('[Mock Fallback] 云主机列表无数据，使用 mock 数据')
      return getMockList(params)
    }
    return res
  }).catch(err => {
    // 后端请求失败，使用 mock
    console.log('[Mock Fallback] 云主机列表请求失败，使用 mock 数据', err.message)
    return getMockList(params)
  })
}

export function fetchFilterOptions() {
  return Promise.resolve({ cpuOptions: [2, 4, 8, 16, 32], memoryOptions: [4, 8, 16, 32, 64, 128] })
}

/**
 * 导出云主机报告
 * @param {Object} params - 查询参数（含 startDate, endDate, 筛选条件）
 * @param {Array} fallbackList - 当后端无数据时，使用当前页面列表数据导出
 */
export function exportCloudVmReport(params, fallbackList) {
  return axios.post(API_BASE_URL + API_PATHS.CLOUD_VM_EXPORT, params, {
    responseType: 'blob',
    timeout: 60000
  }).then(response => {
    // 检查后端返回的是否是错误 JSON
    const contentType = response.headers['content-type'] || ''
    if (contentType.includes('application/json')) {
      console.log('[Mock Fallback] 后端导出返回错误，使用页面数据导出')
      if (fallbackList && fallbackList.length > 0) {
        return exportMockListExcel(fallbackList, params.startDate, params.endDate)
      }
      return { code: 500, message: '无数据可导出' }
    }
    // 解析 Excel 检查数据行数
    return checkExcelAndDownload(response, fallbackList, params.startDate, params.endDate, 'list')
  }).catch(err => {
    // 后端请求失败，使用页面数据导出
    console.log('[Mock Fallback] 后端导出请求失败，使用页面数据导出', err.message)
    if (fallbackList && fallbackList.length > 0) {
      return exportMockListExcel(fallbackList, params.startDate, params.endDate)
    }
    return Promise.reject(err)
  })
}

// ==================== 主机详情 ====================

export function fetchServerDetail(serverId) {
  return request.get(`${API_PATHS.CLOUD_VM_DETAIL}/${serverId}`).then(res => {
    // 后端返回非200或数据为空，使用 mock
    if (res.code !== 200 || !res.data) {
      console.log('[Mock Fallback] 主机详情无数据，使用 mock 数据')
      return getMockDetail(serverId)
    }
    return res
  }).catch(err => {
    // 后端请求失败，使用 mock
    console.log('[Mock Fallback] 主机详情请求失败，使用 mock 数据', err.message)
    return getMockDetail(serverId)
  })
}

export function fetchServerMetricData(serverId, params) {
  return request.get(`${API_PATHS.CLOUD_VM_METRIC_DATA}/${serverId}`, { params }).then(res => {
    // 后端返回非200或数据为空，使用 mock
    if (res.code !== 200 || !res.data || res.data.length === 0) {
      console.log('[Mock Fallback] 监控数据无数据，使用 mock 数据')
      return getMockMetricData(serverId, params)
    }
    return res
  }).catch(err => {
    // 后端请求失败，使用 mock
    console.log('[Mock Fallback] 监控数据请求失败，使用 mock 数据', err.message)
    return getMockMetricData(serverId, params)
  })
}

/**
 * 导出单主机监控数据
 * @param {string} serverId
 * @param {Object} params - 含 startDate, endDate, period
 * @param {string} hostName - 主机名称，用于 fallback 导出时文件命名
 * @param {Array} fallbackMetricData - 当后端无数据时，使用当前页面监控数据导出
 */
export function exportServerMetric(serverId, params, hostName, fallbackMetricData) {
  return axios.get(`${API_BASE_URL}${API_PATHS.CLOUD_VM_EXPORT_METRIC}/${serverId}`, {
    params,
    responseType: 'blob',
    timeout: 60000
  }).then(response => {
    // 检查后端返回的是否是错误 JSON
    const contentType = response.headers['content-type'] || ''
    if (contentType.includes('application/json')) {
      console.log('[Mock Fallback] 后端监控导出返回错误，使用页面数据导出')
      if (fallbackMetricData && fallbackMetricData.length > 0) {
        return exportMockMetricExcel(hostName, fallbackMetricData, params.startDate, params.endDate)
      }
      return { code: 500, message: '无数据可导出' }
    }
    // 解析 Excel 检查数据行数
    return checkExcelAndDownload(response, { hostName, metricData: fallbackMetricData, startDate: params.startDate, endDate: params.endDate }, null, null, 'metric')
  }).catch(err => {
    // 后端请求失败，使用页面数据导出
    console.log('[Mock Fallback] 后端监控导出请求失败，使用页面数据导出', err.message)
    if (fallbackMetricData && fallbackMetricData.length > 0) {
      return exportMockMetricExcel(hostName, fallbackMetricData, params.startDate, params.endDate)
    }
    return Promise.reject(err)
  })
}

// ==================== 鉴权配置 ====================

export function fetchConfigList() {
  return request.get(API_PATHS.CONFIG_LIST)
}

export function addConfig(data) {
  return request.post(API_PATHS.CONFIG_ADD, data)
}

export function updateConfig(data) {
  return request.put(API_PATHS.CONFIG_UPDATE, data)
}

export function deleteConfig(params) {
  return request.delete(API_PATHS.CONFIG_DELETE, { params })
}

export function refreshConfigResources(params) {
  return request.post(API_PATHS.CONFIG_REFRESH, null, { params })
}

// ==================== 解析规则 ====================

export function fetchParseRules() {
  return request.get(API_PATHS.PARSE_RULES_LIST)
}

export function addParseRule(data) {
  return request.post(API_PATHS.PARSE_RULES_ADD, data)
}

export function updateParseRule(data) {
  return request.put(API_PATHS.PARSE_RULES_UPDATE, data)
}

export function deleteParseRule(params) {
  return request.delete(API_PATHS.PARSE_RULES_DELETE, { params })
}

// ==================== 定时任务配置 ====================

export function fetchSchedulerConfig() {
  return request.get(API_PATHS.SCHEDULER_CONFIG)
}

export function updateSchedulerConfig(data) {
  return request.put(API_PATHS.SCHEDULER_UPDATE, data)
}
