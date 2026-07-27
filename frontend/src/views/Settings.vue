<template>
  <div class="settings-page">
    <div class="page-header">
      <div class="page-header-left">
        <el-icon class="back-icon" @click="$router.push('/cloud-vm')"><ArrowLeft /></el-icon>
        <h3>系统设置</h3>
      </div>
    </div>

    <el-tabs v-model="activeTab" class="settings-tabs">
      <el-tab-pane label="解析规则" name="parseRule">
        <div class="tab-header">
          <span class="tab-desc">配置云主机名称解析规则。未配置解析规则时，不解析云主机名称，委办局和应用系统字段为空。如果云主机有统一的命名规则（如 {部门名称}_{应用系统}_{主机用途}），配置后程序会在下次刷新云主机数据时自动解析。名称前缀为空时解析所有云主机，不为空时只解析以该前缀开头的云主机。按列表顺序依次匹配，匹配到第一条即停止，建议将有前缀的规则排在空前缀规则之前。</span>
        </div>
        <el-table :data="parseRuleList" border stripe style="width: 100%">
          <el-table-column prop="namePrefix" label="名称前缀" min-width="300">
            <template #default="{ row }">
              <span>{{ row.namePrefix || '（空，解析所有云主机）' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" align="center">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="handleEditParseRule(row)">编辑</el-button>
              <el-popconfirm title="确定删除该解析规则？" @confirm="handleDeleteParseRule(row)">
                <template #reference>
                  <el-button type="danger" link size="small">删除</el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
        <div class="add-rule-btn">
          <el-button type="primary" size="small" @click="handleAddParseRule">
            <el-icon><Plus /></el-icon>新增规则
          </el-button>
        </div>
      </el-tab-pane>
      <el-tab-pane label="定时任务" name="scheduler">
        <div class="tab-header">
          <span class="tab-desc">每天定时刷新云主机和云硬盘数据，获取前一天的使用率数据，如需更改任务执行时间，请在下方选择任务开始执行的时间。</span>
        </div>
        <el-form :model="schedulerForm" label-width="120px" class="scheduler-form" v-loading="schedulerLoading">
          <el-form-item label="执行时间">
            <el-time-picker v-model="schedulerTime" format="HH:mm" placeholder="选择执行时间" :clearable="false" style="width: 180px" />
            <span class="time-preview">每天 {{ timePreview }} 执行</span>
          </el-form-item>
          <el-form-item label="数据粒度">
            <el-select v-model="schedulerForm.metricPeriod" placeholder="选择数据粒度" style="width: 180px">
              <el-option :value="60" label="1分钟" />
              <el-option :value="300" label="5分钟" />
              <el-option :value="1200" label="20分钟" />
              <el-option :value="3600" label="1小时" />
              <el-option :value="14400" label="4小时" />
              <el-option :value="86400" label="1天" />
            </el-select>
            <a class="period-help-link" href="https://support.huaweicloud.com/api-ces/ces_03_0034.html#section5" target="_blank">了解数据粒度说明</a>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSaveScheduler" :loading="schedulerSaveLoading">保存</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
      <el-tab-pane label="鉴权设置" name="authConfig">
        <div class="tab-header">
          <span class="tab-desc">管理华为云租户鉴权信息</span>
          <el-button type="primary" size="small" @click="handleAddConfig">
            <el-icon><Plus /></el-icon>新增鉴权
          </el-button>
        </div>
        <el-table :data="configList" border stripe style="width: 100%">
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
              <el-button type="primary" link size="small" @click="handleEditConfig(row)">编辑</el-button>
              <el-button type="success" link size="small" @click="handleRefreshConfig(row)" :loading="row._refreshing">刷新资源</el-button>
              <el-popconfirm title="确定删除该鉴权配置？" @confirm="handleDeleteConfig(row)">
                <template #reference>
                  <el-button type="danger" link size="small">删除</el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- 解析规则编辑弹窗 -->
    <el-dialog v-model="parseRuleDialogVisible" :title="isEditParseRule ? '编辑解析规则' : '新增解析规则'" width="480px" destroy-on-close>
      <el-form ref="parseRuleFormRef" :model="parseRuleForm" label-width="100px">
        <el-form-item label="名称前缀">
          <el-input v-model="parseRuleForm.namePrefix" placeholder="留空则解析所有云主机" />
          <div class="form-tip">前缀为空时，按 {部门}_{应用系统}_{主机用途} 格式解析所有云主机；前缀不为空时，只解析以该前缀开头的云主机</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="parseRuleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitParseRule" :loading="parseRuleSubmitLoading">确定</el-button>
      </template>
    </el-dialog>

    <!-- 鉴权配置编辑弹窗 -->
    <el-dialog v-model="configDialogVisible" :title="isEditConfig ? '编辑鉴权' : '新增鉴权'" width="560px" destroy-on-close>
      <el-form ref="configFormRef" :model="configForm" :rules="configRules" label-width="100px">
        <el-form-item label="区域名称" prop="regionName">
          <el-input v-model="configForm.regionName" placeholder="请输入区域名称" :disabled="isEditConfig" />
        </el-form-item>
        <el-form-item label="API端点" prop="endpoint">
          <el-input v-model="configForm.endpoint" placeholder="请输入API端点" :disabled="isEditConfig" />
        </el-form-item>
        <el-form-item label="项目ID" prop="projectId">
          <el-input v-model="configForm.projectId" placeholder="请输入项目ID" :disabled="isEditConfig" />
        </el-form-item>
        <el-form-item label="Access Key" prop="ak">
          <el-input v-model="configForm.ak" placeholder="请输入Access Key" />
        </el-form-item>
        <el-form-item label="Secret Key" prop="sk">
          <el-input v-model="configForm.sk" placeholder="请输入Secret Key" type="password" show-password />
        </el-form-item>
        <el-form-item label="网络分区" prop="networkZone">
          <el-input v-model="configForm.networkZone" placeholder="请输入网络分区" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="configDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitConfig" :loading="configSubmitLoading">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { fetchConfigList, addConfig, updateConfig, deleteConfig, refreshConfigResources, fetchParseRules, addParseRule, updateParseRule, deleteParseRule, fetchSchedulerConfig, updateSchedulerConfig } from '@/api/cloudVm'

const router = useRouter()
const activeTab = ref('parseRule')

// --- 解析规则 ---
const parseRuleList = ref([])
const parseRuleDialogVisible = ref(false)
const isEditParseRule = ref(false)
const parseRuleSubmitLoading = ref(false)
const parseRuleFormRef = ref(null)

const parseRuleForm = reactive({
  id: null,
  namePrefix: ''
})

async function loadParseRules() {
  try {
    const res = await fetchParseRules()
    if (res.code === 200) {
      parseRuleList.value = res.data || []
    }
  } catch (e) {
    console.error('获取解析规则失败', e)
  }
}

function handleAddParseRule() {
  isEditParseRule.value = false
  Object.assign(parseRuleForm, { id: null, namePrefix: '' })
  parseRuleDialogVisible.value = true
}

function handleEditParseRule(row) {
  isEditParseRule.value = true
  Object.assign(parseRuleForm, {
    id: row.id,
    namePrefix: row.namePrefix || ''
  })
  parseRuleDialogVisible.value = true
}

async function handleSubmitParseRule() {
  parseRuleSubmitLoading.value = true
  try {
    const data = {
      namePrefix: parseRuleForm.namePrefix,
      departmentIndex: 0,
      appSystemIndex: 1,
      enabled: 1
    }
    let res
    if (isEditParseRule.value) {
      res = await updateParseRule({ id: parseRuleForm.id, ...data })
    } else {
      res = await addParseRule(data)
    }
    if (res.code === 200) {
      ElMessage.success(isEditParseRule.value ? '更新成功' : '新增成功')
      parseRuleDialogVisible.value = false
      loadParseRules()
    } else {
      ElMessage.error(res.message || '操作失败')
    }
  } catch (e) {
    ElMessage.error('操作失败')
  } finally {
    parseRuleSubmitLoading.value = false
  }
}

async function handleDeleteParseRule(row) {
  try {
    const res = await deleteParseRule({ id: row.id })
    if (res.code === 200) {
      ElMessage.success('删除成功')
      loadParseRules()
    } else {
      ElMessage.error(res.message || '删除失败')
    }
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

// --- 定时任务配置 ---
const schedulerLoading = ref(false)
const schedulerSaveLoading = ref(false)
const schedulerTime = ref(new Date(2026, 0, 1, 2, 0, 0)) // 默认凌晨2点
const schedulerForm = reactive({
  id: null,
  cronExpr: '0 0 2 * * ?',
  metricPeriod: 300
})

const timePreview = computed(() => {
  const d = schedulerTime.value
  if (!d) return '02:00'
  const h = String(d.getHours()).padStart(2, '0')
  const m = String(d.getMinutes()).padStart(2, '0')
  return `${h}:${m}`
})

function timeToCron(date) {
  const minute = date.getMinutes()
  const hour = date.getHours()
  return `0 ${minute} ${hour} * * ?`
}

function cronToTime(cronExpr) {
  const parts = cronExpr.trim().split(/\s+/)
  if (parts.length === 6) {
    const minute = parseInt(parts[1], 10) || 0
    const hour = parseInt(parts[2], 10) || 0
    return new Date(2026, 0, 1, hour, minute, 0)
  }
  return new Date(2026, 0, 1, 2, 0, 0)
}

async function loadSchedulerConfig() {
  schedulerLoading.value = true
  try {
    const res = await fetchSchedulerConfig()
    if (res.code === 200 && res.data) {
      schedulerForm.id = res.data.id
      schedulerForm.cronExpr = res.data.cronExpr || '0 0 2 * * ?'
      schedulerForm.metricPeriod = res.data.metricPeriod || 300
      schedulerTime.value = cronToTime(schedulerForm.cronExpr)
    }
  } catch (e) {
    console.error('获取定时任务配置失败', e)
  } finally {
    schedulerLoading.value = false
  }
}

async function handleSaveScheduler() {
  const cronExpr = timeToCron(schedulerTime.value)
  schedulerSaveLoading.value = true
  try {
    const res = await updateSchedulerConfig({
      id: schedulerForm.id,
      cronExpr,
      metricPeriod: schedulerForm.metricPeriod
    })
    if (res.code === 200) {
      ElMessage.success('保存成功')
      schedulerForm.cronExpr = cronExpr
      if (res.data) {
        schedulerForm.id = res.data.id
      }
    } else {
      ElMessage.error(res.message || '保存失败')
    }
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    schedulerSaveLoading.value = false
  }
}

// --- 鉴权配置 ---
const configList = ref([])
const configDialogVisible = ref(false)
const isEditConfig = ref(false)
const configSubmitLoading = ref(false)
const configFormRef = ref(null)

const configForm = reactive({
  regionName: '',
  endpoint: '',
  projectId: '',
  ak: '',
  sk: '',
  networkZone: ''
})

const configRules = {
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
  try {
    const res = await fetchConfigList()
    if (res.code === 200) {
      configList.value = (res.data || []).map(item => ({ ...item, _refreshing: false }))
    }
  } catch (e) {
    ElMessage.error('获取鉴权配置失败')
  }
}

function handleAddConfig() {
  isEditConfig.value = false
  Object.assign(configForm, { regionName: '', endpoint: '', projectId: '', ak: '', sk: '', networkZone: '' })
  configDialogVisible.value = true
}

function handleEditConfig(row) {
  isEditConfig.value = true
  Object.assign(configForm, {
    regionName: row.regionName,
    endpoint: row.endpoint,
    projectId: row.projectId,
    ak: row.ak,
    sk: row.sk,
    networkZone: row.networkZone || ''
  })
  configDialogVisible.value = true
}

async function handleSubmitConfig() {
  const valid = await configFormRef.value.validate().catch(() => false)
  if (!valid) return

  configSubmitLoading.value = true
  try {
    let res
    if (isEditConfig.value) {
      res = await updateConfig(configForm)
    } else {
      res = await addConfig(configForm)
    }
    if (res.code === 200) {
      ElMessage.success(isEditConfig.value ? '更新成功' : '新增成功')
      configDialogVisible.value = false
      loadConfigList()
    } else {
      ElMessage.error(res.message || '操作失败')
    }
  } catch (e) {
    ElMessage.error('操作失败')
  } finally {
    configSubmitLoading.value = false
  }
}

async function handleDeleteConfig(row) {
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

async function handleRefreshConfig(row) {
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
  loadParseRules()
  loadSchedulerConfig()
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

.page-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-header-left h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.back-icon {
  font-size: 20px;
  color: #606266;
  cursor: pointer;
  transition: color 0.2s;
}

.back-icon:hover {
  color: #409eff;
}

.settings-tabs {
  margin-top: 4px;
}

.tab-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.tab-desc {
  font-size: 13px;
  color: #909399;
  flex: 1;
  margin-right: 12px;
}

.add-rule-btn {
  margin-top: 12px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  line-height: 1.5;
}

.scheduler-form {
  max-width: 600px;
}

.time-preview {
  margin-left: 12px;
  font-size: 13px;
  color: #67c23a;
}

.period-help-link {
  margin-left: 12px;
  font-size: 13px;
  color: #409eff;
  text-decoration: none;
}

.period-help-link:hover {
  text-decoration: underline;
}
</style>
