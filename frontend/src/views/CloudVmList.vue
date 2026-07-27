<template>
  <div class="cloud-vm-page">
    <div class="search-area">
      <el-form :model="searchForm" inline class="search-form" label-width="auto">
        <el-form-item label="委办局">
          <el-input v-model="searchForm.department" placeholder="请输入委办局" clearable style="width: 160px" />
        </el-form-item>
        <el-form-item label="应用系统">
          <el-input v-model="searchForm.appSystem" placeholder="请输入应用系统" clearable style="width: 160px" />
        </el-form-item>
        <el-form-item label="主机名称">
          <el-input v-model="searchForm.hostName" placeholder="请输入主机名称" clearable style="width: 160px" />
        </el-form-item>
        <el-form-item label="IP地址">
          <el-input v-model="searchForm.ipAddress" placeholder="请输入IP地址" clearable style="width: 160px" />
        </el-form-item>
        <el-form-item label="主机状态">
          <el-select v-model="searchForm.status" placeholder="请选择" clearable style="width: 120px">
            <el-option v-for="item in filterOptions.statusOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="CPU核数">
          <el-select v-model="searchForm.cpu" placeholder="请选择" clearable style="width: 120px">
            <el-option v-for="item in filterOptions.cpuOptions" :key="item" :label="item + '核'" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="内存大小">
          <el-select v-model="searchForm.memory" placeholder="请选择" clearable style="width: 120px">
            <el-option v-for="item in filterOptions.memoryOptions" :key="item" :label="item + 'GB'" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="系统盘(GB)">
          <div class="range-input">
            <el-input-number v-model="searchForm.systemDiskMin" :min="0" :controls="false" placeholder="最小" style="width: 90px" />
            <span class="range-separator">-</span>
            <el-input-number v-model="searchForm.systemDiskMax" :min="0" :controls="false" placeholder="最大" style="width: 90px" />
          </div>
        </el-form-item>
        <el-form-item label="数据盘(GB)">
          <div class="range-input">
            <el-input-number v-model="searchForm.dataDiskMin" :min="0" :controls="false" placeholder="最小" style="width: 90px" />
            <span class="range-separator">-</span>
            <el-input-number v-model="searchForm.dataDiskMax" :min="0" :controls="false" placeholder="最大" style="width: 90px" />
          </div>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><RefreshRight /></el-icon>重置
          </el-button>
          <el-button type="success" @click="handleExport">
            <el-icon><Download /></el-icon>导出报告
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="table-area">
      <el-table :data="tableData" border stripe v-loading="loading" style="width: 100%" max-height="calc(100vh - 320px)" @row-click="handleRowClick">
        <el-table-column prop="hostName" label="主机名称" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="host-name-link">{{ row.hostName }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="department" label="委办局" min-width="120" show-overflow-tooltip />
        <el-table-column prop="appSystem" label="应用系统" min-width="140" show-overflow-tooltip />
        <el-table-column prop="ipAddress" label="IP地址" min-width="130" />
        <el-table-column prop="status" label="状态" min-width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="os" label="操作系统" min-width="140" show-overflow-tooltip />
        <el-table-column prop="spec" label="规格" min-width="130" show-overflow-tooltip />
        <el-table-column prop="architecture" label="CPU架构" min-width="90" align="center" />
        <el-table-column prop="region" label="区域" min-width="120" show-overflow-tooltip />
        <el-table-column prop="cpu" label="CPU（核）" min-width="90" align="center" />
        <el-table-column prop="memory" label="内存（GB）" min-width="100" align="center" />
        <el-table-column prop="systemDisk" label="系统盘（GB）" min-width="110" align="center" />
        <el-table-column prop="dataDisk" label="数据盘（GB）" min-width="110" align="center" />
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
import { fetchCloudVmList, fetchFilterOptions } from '@/api/cloudVm'
import ExportDialog from '@/components/ExportDialog.vue'

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
  const map = { '运行中': 'success', '已关机': 'info', '异常': 'danger' }
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
    ElMessage.error('获取数据失败')
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
    console.error('获取筛选选项失败', e)
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
  ElMessage.success('报告导出成功')
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
