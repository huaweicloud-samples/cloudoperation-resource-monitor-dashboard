<template>
  <div class="server-detail-page">
    <div class="page-header">
      <el-button @click="goBack" :icon="ArrowLeft" text>{{ $t('server_detail.back_to_list') }}</el-button>
      <h3>{{ detail.hostName || $t('server_detail.page_title') }}</h3>
    </div>

    <div v-loading="detailLoading" class="detail-section">
      <h4 class="section-title">{{ $t('server_detail.basic_info') }}</h4>
      <el-descriptions :column="3" border size="default">
        <el-descriptions-item :label="$t('cloud_vm.host_name')">{{ detail.hostName || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="$t('server_detail.running_status')">
          <el-tag :type="statusTagType(detail.status)" size="small">{{ detail.status || '-' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item :label="$t('server_detail.department')">{{ detail.department || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="$t('server_detail.app_system')">{{ detail.appSystem || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="$t('server_detail.region_name')">{{ detail.regionName || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="$t('server_detail.network_zone')">{{ detail.networkZone || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="$t('server_detail.ipv4')">{{ detail.ipAddress || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="$t('server_detail.ipv6')">{{ detail.ipv6 || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="$t('server_detail.public_eip')">{{ detail.publicEip || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="$t('cloud_vm.os')">{{ detail.os || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="$t('server_detail.os_version')">{{ detail.osName || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="$t('server_detail.image_name')">{{ detail.imageName || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="$t('server_detail.vm_spec')">{{ detail.spec || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="$t('cloud_vm.cpu_arch')">{{ detail.architecture || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="$t('server_detail.availability_zone')">{{ detail.availabilityZone || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="$t('server_detail.cpu_cores')">{{ detail.cpu || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="$t('server_detail.memory_gb')">{{ detail.memory || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="$t('server_detail.created_at')">{{ detail.createdAt || '-' }}</el-descriptions-item>
      </el-descriptions>

      <template v-if="detail.volumes && detail.volumes.length > 0">
        <h4 class="section-title" style="margin-top: 20px;">{{ $t('server_detail.disk_info') }}</h4>
        <el-table :data="detail.volumes" border size="small" style="width: 100%">
          <el-table-column prop="name" :label="$t('server_detail.disk_name')" min-width="140" show-overflow-tooltip />
          <el-table-column prop="size" :label="$t('server_detail.disk_size')" width="100" align="center" />
          <el-table-column prop="volumeType" :label="$t('server_detail.disk_type')" width="100" align="center" />
          <el-table-column prop="ioLabel" :label="$t('server_detail.io_type')" width="100" align="center" />
          <el-table-column prop="diskType" :label="$t('server_detail.disk_category')" width="100" align="center" />
        </el-table>
      </template>
    </div>

    <div class="metric-section">
      <div class="metric-header">
        <h4 class="section-title">{{ $t('server_detail.metric_data') }}</h4>
        <div class="metric-controls">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            :range-separator="$t('common.to')"
            :start-placeholder="$t('server_detail.start_date')"
            :end-placeholder="$t('server_detail.end_date')"
            value-format="YYYY-MM-DD"
            :disabled-date="disabledDate"
            style="width: 280px"
            @change="loadMetricData"
          />
          <el-select v-model="period" style="width: 120px" @change="loadMetricData">
            <el-option :label="$t('server_detail.period_5min')" value="5min" />
            <el-option :label="$t('server_detail.period_day')" value="day" />
          </el-select>
          <el-button type="success" @click="handleExportMetric" :loading="exportLoading" :icon="Download">{{ $t('server_detail.export_data') }}</el-button>
        </div>
      </div>

      <div v-loading="metricLoading" class="metric-charts">
        <div v-if="metricData.length === 0 && !metricLoading" class="no-data">{{ $t('server_detail.no_metric_data') }}</div>
        <template v-else>
          <div class="chart-container">
            <div class="chart-title">{{ $t('server_detail.cpu_usage') }}</div>
            <div class="chart-wrapper" ref="cpuChartRef"></div>
          </div>
          <div class="chart-container">
            <div class="chart-title">{{ $t('server_detail.mem_usage') }}</div>
            <div class="chart-wrapper" ref="memChartRef"></div>
          </div>
          <div class="chart-container">
            <div class="chart-title">{{ $t('server_detail.disk_usage') }}</div>
            <div class="chart-wrapper" ref="diskChartRef"></div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'
import { fetchServerDetail, fetchServerMetricData, exportServerMetric } from '@/api/cloudVm'
import dayjs from 'dayjs'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const serverId = route.params.id

const detailLoading = ref(false)
const metricLoading = ref(false)
const exportLoading = ref(false)
const detail = reactive({})
const metricData = ref([])

const dateRange = ref([])
const period = ref('5min')

const cpuChartRef = ref(null)
const memChartRef = ref(null)
const diskChartRef = ref(null)

let cpuChart = null
let memChart = null
let diskChart = null

function statusTagType(status) {
  const map = { '运行中': 'success', '已关机': 'info', '异常': 'danger', 'Running': 'success', 'Stopped': 'info', 'Error': 'danger' }
  return map[status] || 'info'
}

const disabledDate = (time) => {
  return time.getTime() > Date.now()
}

function goBack() {
  router.push('/cloud-vm')
}

async function loadDetail() {
  detailLoading.value = true
  try {
    const res = await fetchServerDetail(serverId)
    if (res.code === 200 && res.data) {
      Object.assign(detail, res.data)
    } else {
      ElMessage.error(res.message || t('server_detail.fetch_detail_fail'))
    }
  } catch (e) {
    ElMessage.error(t('server_detail.fetch_detail_fail'))
  } finally {
    detailLoading.value = false
  }
}

async function loadMetricData() {
  if (!dateRange.value || dateRange.value.length !== 2) return

  metricLoading.value = true
  try {
    const res = await fetchServerMetricData(serverId, {
      startDate: dateRange.value[0],
      endDate: dateRange.value[1],
      period: period.value
    })
    if (res.code === 200) {
      metricData.value = res.data || []
      await nextTick()
      renderCharts()
    }
  } catch (e) {
    ElMessage.error(t('server_detail.fetch_metric_fail'))
  } finally {
    metricLoading.value = false
  }
}

async function handleExportMetric() {
  if (!dateRange.value || dateRange.value.length !== 2) {
    ElMessage.warning(t('server_detail.select_time_range'))
    return
  }
  exportLoading.value = true
  try {
    await exportServerMetric(serverId, {
      startDate: dateRange.value[0],
      endDate: dateRange.value[1],
      period: period.value
    }, detail.hostName, metricData.value)
    ElMessage.success(t('common.export_success'))
  } catch (e) {
    ElMessage.error(t('common.export_fail'))
  } finally {
    exportLoading.value = false
  }
}

function renderCharts() {
  if (typeof window === 'undefined') return

  const timestamps = metricData.value.map(d => {
    const ts = d.timestamp || ''
    return ts.length > 19 ? ts.substring(0, 19) : ts
  })

  renderChart(cpuChartRef, cpuChart, 'cpuChart', timestamps, [
    { name: t('server_detail.peak'), data: metricData.value.map(d => d.cpuUtilMax), color: '#f56c6c' },
    { name: t('server_detail.average'), data: metricData.value.map(d => d.cpuUtilAvg), color: '#409eff' },
    { name: t('server_detail.minimum'), data: metricData.value.map(d => d.cpuUtilMin), color: '#67c23a' },
  ])

  renderChart(memChartRef, memChart, 'memChart', timestamps, [
    { name: t('server_detail.peak'), data: metricData.value.map(d => d.memUtilMax), color: '#f56c6c' },
    { name: t('server_detail.average'), data: metricData.value.map(d => d.memUtilAvg), color: '#409eff' },
    { name: t('server_detail.minimum'), data: metricData.value.map(d => d.memUtilMin), color: '#67c23a' },
  ])

  renderChart(diskChartRef, diskChart, 'diskChart', timestamps, [
    { name: t('server_detail.peak'), data: metricData.value.map(d => d.diskUtilMax), color: '#f56c6c' },
    { name: t('server_detail.average'), data: metricData.value.map(d => d.diskUtilAvg), color: '#409eff' },
    { name: t('server_detail.minimum'), data: metricData.value.map(d => d.diskUtilMin), color: '#67c23a' },
  ])
}

function renderChart(containerRef, chartInstance, chartKey, xData, seriesList) {
  const container = containerRef.value
  if (!container) return

  const canvas = document.createElement('canvas')
  const width = container.clientWidth || 800
  const height = 260
  canvas.width = width * 2
  canvas.height = height * 2
  canvas.style.width = width + 'px'
  canvas.style.height = height + 'px'
  container.innerHTML = ''
  container.appendChild(canvas)

  const ctx = canvas.getContext('2d')
  ctx.scale(2, 2)

  const padding = { top: 30, right: 20, bottom: 40, left: 50 }
  const chartWidth = width - padding.left - padding.right
  const chartHeight = height - padding.top - padding.bottom

  ctx.fillStyle = '#fafafa'
  ctx.fillRect(0, 0, width, height)

  let maxVal = 0
  for (const s of seriesList) {
    for (const v of s.data) {
      if (v > maxVal) maxVal = v
    }
  }
  maxVal = Math.max(maxVal, 10)
  const yMax = Math.ceil(maxVal / 10) * 10 + 10

  ctx.strokeStyle = '#e4e7ed'
  ctx.lineWidth = 0.5
  const ySteps = 5
  for (let i = 0; i <= ySteps; i++) {
    const y = padding.top + (chartHeight / ySteps) * i
    ctx.beginPath()
    ctx.moveTo(padding.left, y)
    ctx.lineTo(padding.left + chartWidth, y)
    ctx.stroke()

    const val = yMax - (yMax / ySteps) * i
    ctx.fillStyle = '#909399'
    ctx.font = '11px sans-serif'
    ctx.textAlign = 'right'
    ctx.fillText(val.toFixed(0), padding.left - 8, y + 4)
  }

  const xLabelCount = Math.min(xData.length, 8)
  const xStep = xData.length > 1 ? Math.floor(xData.length / xLabelCount) : 1
  ctx.fillStyle = '#909399'
  ctx.font = '10px sans-serif'
  ctx.textAlign = 'center'
  for (let i = 0; i < xData.length; i += xStep) {
    const x = padding.left + (chartWidth / Math.max(xData.length - 1, 1)) * i
    const label = xData[i].replace(/^\d{4}-/, '').replace(/:\d{2}$/, '')
    ctx.fillText(label, x, height - padding.bottom + 20)
  }

  for (const s of seriesList) {
    if (s.data.length === 0) continue
    ctx.strokeStyle = s.color
    ctx.lineWidth = 1.5
    ctx.beginPath()
    for (let i = 0; i < s.data.length; i++) {
      const x = padding.left + (chartWidth / Math.max(s.data.length - 1, 1)) * i
      const y = padding.top + chartHeight - (s.data[i] / yMax) * chartHeight
      if (i === 0) ctx.moveTo(x, y)
      else ctx.lineTo(x, y)
    }
    ctx.stroke()
  }

  let legendX = padding.left
  for (const s of seriesList) {
    ctx.fillStyle = s.color
    ctx.fillRect(legendX, 8, 16, 3)
    ctx.fillStyle = '#606266'
    ctx.font = '11px sans-serif'
    ctx.textAlign = 'left'
    ctx.fillText(s.name, legendX + 20, 14)
    legendX += 70
  }
}

onMounted(() => {
  const end = dayjs()
  const start = end.subtract(1, 'day')
  dateRange.value = [start.format('YYYY-MM-DD'), end.format('YYYY-MM-DD')]

  loadDetail()
  loadMetricData()
})

onUnmounted(() => {
  cpuChart = null
  memChart = null
  diskChart = null
})
</script>

<style scoped>
.server-detail-page {
  padding: 20px;
  background: #fff;
  min-height: calc(100vh - 50px);
}

.page-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.page-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.section-title {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.detail-section {
  margin-bottom: 24px;
}

.metric-section {
  margin-top: 24px;
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.metric-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.metric-charts {
  min-height: 200px;
}

.no-data {
  text-align: center;
  color: #909399;
  padding: 60px 0;
  font-size: 14px;
}

.chart-container {
  margin-bottom: 20px;
}

.chart-title {
  font-size: 13px;
  font-weight: 500;
  color: #606266;
  margin-bottom: 8px;
}

.chart-wrapper {
  width: 100%;
  height: 260px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  overflow: hidden;
}
</style>
