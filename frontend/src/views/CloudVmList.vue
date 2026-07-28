<template>
  <div class="cloud-vm-page">
    <div class="search-area">
      <el-form :model="searchForm" inline class="search-form" label-width="auto">
        <el-form-item :label="$t('cloud_vm.department')">
          <el-input v-model="searchForm.department" :placeholder="$t('cloud_vm.enter_department')" clearable style="width: 160px" />
        </el-form-item>
        <el-form-item :label="$t('cloud_vm.app_system')">
          <el-input v-model="searchForm.appSystem" :placeholder="$t('cloud_vm.enter_app_system')" clearable style="width: 160px" />
        </el-form-item>
        <el-form-item :label="$t('cloud_vm.host_name')">
          <el-input v-model="searchForm.hostName" :placeholder="$t('cloud_vm.enter_host_name')" clearable style="width: 160px" />
        </el-form-item>
        <el-form-item :label="$t('cloud_vm.ip_address')">
          <el-input v-model="searchForm.ipAddress" :placeholder="$t('cloud_vm.enter_ip_address')" clearable style="width: 160px" />
        </el-form-item>
        <el-form-item :label="$t('cloud_vm.host_status')">
          <el-select v-model="searchForm.status" :placeholder="$t('common.select')" clearable style="width: 120px">
            <el-option v-for="item in filterOptions.statusOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('cloud_vm.cpu_cores')">
          <el-select v-model="searchForm.cpu" :placeholder="$t('common.select')" clearable style="width: 120px">
            <el-option v-for="item in filterOptions.cpuOptions" :key="item" :label="item + $t('common.cores')" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('cloud_vm.memory_size')">
          <el-select v-model="searchForm.memory" :placeholder="$t('common.select')" clearable style="width: 120px">
            <el-option v-for="item in filterOptions.memoryOptions" :key="item" :label="item + 'GB'" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('cloud_vm.system_disk_gb')">
          <div class="range-input">
            <el-input-number v-model="searchForm.systemDiskMin" :min="0" :controls="false" :placeholder="$t('common.min')" style="width: 90px" />
            <span class="range-separator">-</span>
            <el-input-number v-model="searchForm.systemDiskMax" :min="0" :controls="false" :placeholder="$t('common.max')" style="width: 90px" />
          </div>
        </el-form-item>
        <el-form-item :label="$t('cloud_vm.data_disk_gb')">
          <div class="range-input">
            <el-input-number v-model="searchForm.dataDiskMin" :min="0" :controls="false" :placeholder="$t('common.min')" style="width: 90px" />
            <span class="range-separator">-</span>
            <el-input-number v-model="searchForm.dataDiskMax" :min="0" :controls="false" :placeholder="$t('common.max')" style="width: 90px" />
          </div>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>{{ $t('common.search') }}
          </el-button>
          <el-button @click="handleReset">
            <el-icon><RefreshRight /></el-icon>{{ $t('common.reset') }}
          </el-button>
          <el-button type="success" @click="handleExport">
            <el-icon><Download /></el-icon>{{ $t('cloud_vm.export_report') }}
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="table-area">
      <el-table :data="tableData" border stripe v-loading="loading" style="width: 100%" max-height="calc(100vh - 320px)" @row-click="handleRowClick">
        <el-table-column prop="hostName" :label="$t('cloud_vm.host_name')" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="host-name-link">{{ row.hostName }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="department" :label="$t('cloud_vm.department')" min-width="120" show-overflow-tooltip />
        <el-table-column prop="appSystem" :label="$t('cloud_vm.app_system')" min-width="140" show-overflow-tooltip />
        <el-table-column prop="ipAddress" :label="$t('cloud_vm.ip_address')" min-width="130" />
        <el-table-column prop="status" :label="$t('common.status')" min-width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="os" :label="$t('cloud_vm.os')" min-width="140" show-overflow-tooltip />
        <el-table-column prop="spec" :label="$t('cloud_vm.spec')" min-width="130" show-overflow-tooltip />
        <el-table-column prop="architecture" :label="$t('cloud_vm.cpu_arch')" min-width="90" align="center" />
        <el-table-column prop="region" :label="$t('cloud_vm.region')" min-width="120" show-overflow-tooltip />
        <el-table-column prop="cpu" :label="$t('cloud_vm.cpu')" min-width="90" align="center" />
        <el-table-column prop="memory" :label="$t('cloud_vm.memory')" min-width="100" align="center" />
        <el-table-column prop="systemDisk" :label="$t('cloud_vm.system_disk')" min-width="110" align="center" />
        <el-table-column prop="dataDisk" :label="$t('cloud_vm.data_disk')" min-width="110" align="center" />
      </el-table>
    </div>

    <div class="pagination-area">
      <el-pagination
        v-model:current-page="pagination.pageNum"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        background
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>

    <ExportDialog ref="exportDialogRef" :search-params="exportSearchParams" :current-list="tableData" @success="onExportSuccess" />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search, RefreshRight, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'
import { fetchCloudVmList, fetchFilterOptions } from '@/api/cloudVm'
import ExportDialog from '@/components/ExportDialog.vue'

const { t } = useI18n()
const router = useRouter()
const loading = ref(false)
const tableData = ref([])
const exportDialogRef = ref(null)

const searchForm = reactive({
  department: '',
  appSystem: '',
  hostName: '',
  ipAddress: '',
  status: '',
  cpu: '',
  memory: '',
  systemDiskMin: undefined,
  systemDiskMax: undefined,
  dataDiskMin: undefined,
  dataDiskMax: undefined
})

const pagination = reactive({
  pageNum: 1,
  pageSize: 10,
  total: 0
})

const filterOptions = reactive({
  cpuOptions: [],
  memoryOptions: [],
  statusOptions: []
})

const allHostIds = computed(() => tableData.value.map(item => item.id))

const exportSearchParams = computed(() => {
  const { ...params } = searchForm
  return params
})

function statusTagType(status) {
  const map = { '运行中': 'success', '已关机': 'info', '异常': 'danger', 'Running': 'success', 'Stopped': 'info', 'Error': 'danger' }
  return map[status] || 'info'
}

function buildParams() {
  return {
    ...searchForm,
    pageNum: pagination.pageNum,
    pageSize: pagination.pageSize
  }
}

async function loadData() {
  loading.value = true
  try {
    const res = await fetchCloudVmList(buildParams())
    if (res.code === 200) {
      tableData.value = res.data.list
      pagination.total = res.data.total
      updateStatusOptions(res.data.list)
    }
  } catch (e) {
    ElMessage.error(t('common.fetch_fail'))
  } finally {
    loading.value = false
  }
}

function updateStatusOptions(list) {
  const statusSet = new Set()
  if (list && list.length > 0) {
    list.forEach(item => {
      if (item.status) statusSet.add(item.status)
    })
  }
  filterOptions.statusOptions.forEach(s => statusSet.add(s))
  filterOptions.statusOptions = [...statusSet].sort()
}

async function loadFilterOptions() {
  try {
    const res = await fetchFilterOptions()
    filterOptions.cpuOptions = res.cpuOptions
    filterOptions.memoryOptions = res.memoryOptions
  } catch (e) {
    console.error('Failed to load filter options', e)
  }
}

function handleSearch() {
  pagination.pageNum = 1
  loadData()
}

function handleReset() {
  Object.assign(searchForm, {
    department: '',
    appSystem: '',
    hostName: '',
    ipAddress: '',
    status: '',
    cpu: '',
    memory: '',
    systemDiskMin: undefined,
    systemDiskMax: undefined,
    dataDiskMin: undefined,
    dataDiskMax: undefined
  })
  pagination.pageNum = 1
  loadData()
}

function handleSizeChange() {
  pagination.pageNum = 1
  loadData()
}

function handlePageChange() {
  loadData()
}

function handleExport() {
  exportDialogRef.value.open()
}

function onExportSuccess() {
  ElMessage.success(t('cloud_vm.export_success'))
}

function handleRowClick(row) {
  router.push(`/cloud-vm/${row.id}`)
}

onMounted(() => {
  loadData()
  loadFilterOptions()
})
</script>

<style scoped>
.cloud-vm-page {
  padding: 20px;
  background: #fff;
  min-height: 100vh;
}

.search-area {
  margin-bottom: 16px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 4px;
}

.search-form :deep(.el-form-item) {
  margin-bottom: 8px;
}

.range-input {
  display: flex;
  align-items: center;
  gap: 4px;
}

.range-separator {
  color: #999;
  font-size: 14px;
}

.table-area {
  margin-bottom: 16px;
}

.pagination-area {
  display: flex;
  justify-content: flex-end;
  padding: 8px 0;
}

.host-name-link {
  color: #409eff;
  cursor: pointer;
}

.host-name-link:hover {
  text-decoration: underline;
}

:deep(.el-table__row) {
  cursor: pointer;
}
</style>
