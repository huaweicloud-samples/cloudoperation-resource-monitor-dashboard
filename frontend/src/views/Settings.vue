<template>
  <div class="settings-page">
    <div class="page-header">
      <h3>鉴权设置</h3>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>新增鉴权
      </el-button>
    </div>

    <el-table :data="configList" border stripe v-loading="loading" style="width: 100%">
      <el-table-column prop="regionName" label="区域名称" min-width="160" show-overflow-tooltip />
      <el-table-column prop="endpoint" label="API端点" min-width="260" show-overflow-tooltip />
      <el-table-column prop="projectId" label="项目ID" min-width="200" show-overflow-tooltip />
      <el-table-column prop="ak" label="Access Key" min-width="160" show-overflow-tooltip>
        <template #default="{ row }">
          <span>{{ maskSecret(row.ak) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="sk" label="Secret Key" min-width="160" show-overflow-tooltip>
        <template #default="{ row }">
          <span>{{ maskSecret(row.sk) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="networkZone" label="网络分区" min-width="100" />
      <el-table-column label="操作" min-width="220" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button type="success" link size="small" @click="handleRefresh(row)" :loading="row._refreshing">刷新资源</el-button>
          <el-popconfirm title="确定删除该鉴权配置？" @confirm="handleDelete(row)">
            <template #reference>
              <el-button type="danger" link size="small">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑鉴权' : '新增鉴权'" width="560px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="区域名称" prop="regionName">
          <el-input v-model="form.regionName" placeholder="请输入区域名称" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="API端点" prop="endpoint">
          <el-input v-model="form.endpoint" placeholder="请输入API端点" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="项目ID" prop="projectId">
          <el-input v-model="form.projectId" placeholder="请输入项目ID" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="Access Key" prop="ak">
          <el-input v-model="form.ak" placeholder="请输入Access Key" />
        </el-form-item>
        <el-form-item label="Secret Key" prop="sk">
          <el-input v-model="form.sk" placeholder="请输入Secret Key" type="password" show-password />
        </el-form-item>
        <el-form-item label="网络分区" prop="networkZone">
          <el-input v-model="form.networkZone" placeholder="请输入网络分区" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { fetchConfigList, addConfig, updateConfig, deleteConfig, refreshConfigResources } from '@/api/cloudVm'

const loading = ref(false)
const configList = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref(null)

const form = reactive({
  regionName: '',
  endpoint: '',
  projectId: '',
  ak: '',
  sk: '',
  networkZone: ''
})

const rules = {
  regionName: [{ required: true, message: '请输入区域名称', trigger: 'blur' }],
  endpoint: [{ required: true, message: '请输入API端点', trigger: 'blur' }],
  projectId: [{ required: true, message: '请输入项目ID', trigger: 'blur' }],
  ak: [{ required: true, message: '请输入Access Key', trigger: 'blur' }],
  sk: [{ required: true, message: '请输入Secret Key', trigger: 'blur' }],
}

function maskSecret(val) {
  if (!val || val.length <= 6) return val || ''
  return val.substring(0, 3) + '****' + val.substring(val.length - 3)
}

async function loadConfigList() {
  loading.value = true
  try {
    const res = await fetchConfigList()
    if (res.code === 200) {
      configList.value = (res.data || []).map(item => ({ ...item, _refreshing: false }))
    }
  } catch (e) {
    ElMessage.error('获取鉴权配置失败')
  } finally {
    loading.value = false
  }
}

function handleAdd() {
  isEdit.value = false
  Object.assign(form, { regionName: '', endpoint: '', projectId: '', ak: '', sk: '', networkZone: '' })
  dialogVisible.value = true
}

function handleEdit(row) {
  isEdit.value = true
  Object.assign(form, {
    regionName: row.regionName,
    endpoint: row.endpoint,
    projectId: row.projectId,
    ak: row.ak,
    sk: row.sk,
    networkZone: row.networkZone || ''
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    let res
    if (isEdit.value) {
      res = await updateConfig(form)
    } else {
      res = await addConfig(form)
    }
    if (res.code === 200) {
      ElMessage.success(isEdit.value ? '更新成功' : '新增成功')
      dialogVisible.value = false
      loadConfigList()
    } else {
      ElMessage.error(res.message || '操作失败')
    }
  } catch (e) {
    ElMessage.error('操作失败')
  } finally {
    submitLoading.value = false
  }
}

async function handleDelete(row) {
  try {
    const res = await deleteConfig({
      regionName: row.regionName,
      endpoint: row.endpoint,
      projectId: row.projectId
    })
    if (res.code === 200) {
      ElMessage.success('删除成功')
      loadConfigList()
    } else {
      ElMessage.error(res.message || '删除失败')
    }
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

async function handleRefresh(row) {
  row._refreshing = true
  try {
    const res = await refreshConfigResources({
      regionName: row.regionName,
      endpoint: row.endpoint,
      projectId: row.projectId
    })
    if (res.code === 200) {
      ElMessage.success('刷新任务已启动，请稍后查看数据更新')
    } else {
      ElMessage.error(res.message || '刷新失败')
    }
  } catch (e) {
    ElMessage.error('刷新失败')
  } finally {
    row._refreshing = false
  }
}

onMounted(() => {
  loadConfigList()
})
</script>

<style scoped>
.settings-page {
  padding: 20px;
  background: #fff;
  min-height: calc(100vh - 50px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.page-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}
</style>
