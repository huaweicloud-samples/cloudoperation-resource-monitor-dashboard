<template>
  <div class="settings-page">
    <div class="page-header">
      <div class="page-header-left">
        <el-icon class="back-icon" @click="$router.push('/cloud-vm')"><ArrowLeft /></el-icon>
        <h3>{{ $t('settings.page_title') }}</h3>
      </div>
    </div>

    <el-tabs v-model="activeTab" class="settings-tabs">
      <el-tab-pane :label="$t('settings.tab_parse_rule')" name="parseRule">
        <div class="tab-header">
          <span class="tab-desc">{{ $t('settings.parse_rule_desc') }}</span>
        </div>
        <el-table :data="parseRuleList" border stripe style="width: 100%">
          <el-table-column prop="namePrefix" :label="$t('settings.name_prefix')" min-width="300">
            <template #default="{ row }">
              <span>{{ row.namePrefix || $t('settings.empty_prefix') }}</span>
            </template>
          </el-table-column>
          <el-table-column :label="$t('common.operation')" width="120" align="center">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="handleEditParseRule(row)">{{ $t('common.edit') }}</el-button>
              <el-popconfirm :title="$t('settings.confirm_delete_rule')" @confirm="handleDeleteParseRule(row)">
                <template #reference>
                  <el-button type="danger" link size="small">{{ $t('common.delete') }}</el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
        <div class="add-rule-btn">
          <el-button type="primary" size="small" @click="handleAddParseRule">
            <el-icon><Plus /></el-icon>{{ $t('settings.add_rule') }}
          </el-button>
        </div>
      </el-tab-pane>
      <el-tab-pane :label="$t('settings.tab_scheduler')" name="scheduler">
        <div class="tab-header">
          <span class="tab-desc">{{ $t('settings.scheduler_desc') }}</span>
        </div>
        <el-form :model="schedulerForm" label-width="120px" class="scheduler-form" v-loading="schedulerLoading">
          <el-form-item :label="$t('settings.execution_time')">
            <el-time-picker v-model="schedulerTime" format="HH:mm" :placeholder="$t('settings.execution_time')" :clearable="false" style="width: 180px" />
            <span class="time-preview">{{ $t('settings.daily_at', { time: timePreview }) }}</span>
          </el-form-item>
          <el-form-item :label="$t('settings.data_granularity')">
            <el-select v-model="schedulerForm.metricPeriod" :placeholder="$t('settings.data_granularity')" style="width: 180px">
              <el-option :value="60" :label="$t('settings.granularity_1min')" />
              <el-option :value="300" :label="$t('settings.granularity_5min')" />
              <el-option :value="1200" :label="$t('settings.granularity_20min')" />
              <el-option :value="3600" :label="$t('settings.granularity_1h')" />
              <el-option :value="14400" :label="$t('settings.granularity_4h')" />
              <el-option :value="86400" :label="$t('settings.granularity_1d')" />
            </el-select>
            <a class="period-help-link" href="https://support.huaweicloud.com/api-ces/ces_03_0034.html#section5" target="_blank">{{ $t('settings.granularity_help') }}</a>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSaveScheduler" :loading="schedulerSaveLoading">{{ $t('common.save') }}</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
      <el-tab-pane :label="$t('settings.tab_auth_config')" name="authConfig">
        <div class="tab-header">
          <span class="tab-desc">{{ $t('settings.auth_desc') }}</span>
          <el-button type="primary" size="small" @click="handleAddConfig">
            <el-icon><Plus /></el-icon>{{ $t('settings.add_auth') }}
          </el-button>
        </div>
        <el-table :data="configList" border stripe style="width: 100%">
          <el-table-column prop="regionName" :label="$t('settings.region_name')" min-width="160" show-overflow-tooltip />
          <el-table-column prop="endpoint" :label="$t('settings.api_endpoint')" min-width="260" show-overflow-tooltip />
          <el-table-column prop="projectId" :label="$t('settings.project_id')" min-width="200" show-overflow-tooltip />
          <el-table-column prop="ak" :label="$t('settings.access_key')" min-width="160" show-overflow-tooltip>
            <template #default="{ row }">
              <span>{{ maskSecret(row.ak) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="sk" :label="$t('settings.secret_key')" min-width="160" show-overflow-tooltip>
            <template #default="{ row }">
              <span>{{ maskSecret(row.sk) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="networkZone" :label="$t('settings.network_zone')" min-width="100" />
          <el-table-column :label="$t('common.operation')" min-width="220" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="handleEditConfig(row)">{{ $t('common.edit') }}</el-button>
              <el-button type="success" link size="small" @click="handleRefreshConfig(row)" :loading="row._refreshing">{{ $t('common.refresh_resources') }}</el-button>
              <el-popconfirm :title="$t('settings.confirm_delete_auth')" @confirm="handleDeleteConfig(row)">
                <template #reference>
                  <el-button type="danger" link size="small">{{ $t('common.delete') }}</el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- 解析规则编辑弹窗 -->
    <el-dialog v-model="parseRuleDialogVisible" :title="isEditParseRule ? $t('settings.edit_rule') : $t('settings.new_rule')" width="480px" destroy-on-close>
      <el-form ref="parseRuleFormRef" :model="parseRuleForm" label-width="100px">
        <el-form-item :label="$t('settings.name_prefix')">
          <el-input v-model="parseRuleForm.namePrefix" :placeholder="$t('settings.prefix_placeholder')" />
          <div class="form-tip">{{ $t('settings.prefix_tip') }}</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="parseRuleDialogVisible = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="handleSubmitParseRule" :loading="parseRuleSubmitLoading">{{ $t('common.confirm') }}</el-button>
      </template>
    </el-dialog>

    <!-- 鉴权配置编辑弹窗 -->
    <el-dialog v-model="configDialogVisible" :title="isEditConfig ? $t('settings.edit_auth') : $t('settings.new_auth')" width="560px" destroy-on-close>
      <el-form ref="configFormRef" :model="configForm" :rules="configRules" label-width="100px">
        <el-form-item :label="$t('settings.region_name')" prop="regionName">
          <el-input v-model="configForm.regionName" :placeholder="$t('settings.enter_region')" :disabled="isEditConfig" />
        </el-form-item>
        <el-form-item :label="$t('settings.api_endpoint')" prop="endpoint">
          <el-input v-model="configForm.endpoint" :placeholder="$t('settings.enter_endpoint')" :disabled="isEditConfig" />
        </el-form-item>
        <el-form-item :label="$t('settings.project_id')" prop="projectId">
          <el-input v-model="configForm.projectId" :placeholder="$t('settings.enter_project_id')" :disabled="isEditConfig" />
        </el-form-item>
        <el-form-item :label="$t('settings.access_key')" prop="ak">
          <el-input v-model="configForm.ak" :placeholder="$t('settings.enter_ak')" />
        </el-form-item>
        <el-form-item :label="$t('settings.secret_key')" prop="sk">
          <el-input v-model="configForm.sk" :placeholder="$t('settings.enter_sk')" type="password" show-password />
        </el-form-item>
        <el-form-item :label="$t('settings.network_zone')" prop="networkZone">
          <el-input v-model="configForm.networkZone" :placeholder="$t('settings.enter_network_zone')" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="configDialogVisible = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="handleSubmitConfig" :loading="configSubmitLoading">{{ $t('common.confirm') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'
import { fetchConfigList, addConfig, updateConfig, deleteConfig, refreshConfigResources, fetchParseRules, addParseRule, updateParseRule, deleteParseRule, fetchSchedulerConfig, updateSchedulerConfig } from '@/api/cloudVm'

const router = useRouter()
const { t } = useI18n()
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
      ElMessage.success(isEditParseRule.value ? t('common.update_success') : t('common.add_success'))
      parseRuleDialogVisible.value = false
      loadParseRules()
    } else {
      ElMessage.error(res.message || t('common.operation_fail'))
    }
  } catch (e) {
    ElMessage.error(t('common.operation_fail'))
  } finally {
    parseRuleSubmitLoading.value = false
  }
}

async function handleDeleteParseRule(row) {
  try {
    const res = await deleteParseRule({ id: row.id })
    if (res.code === 200) {
      ElMessage.success(t('common.delete_success'))
      loadParseRules()
    } else {
      ElMessage.error(res.message || t('common.delete_fail'))
    }
  } catch (e) {
    ElMessage.error(t('common.delete_fail'))
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
      ElMessage.success(t('common.save_success'))
      schedulerForm.cronExpr = cronExpr
      if (res.data) {
        schedulerForm.id = res.data.id
      }
    } else {
      ElMessage.error(res.message || t('common.save_fail'))
    }
  } catch (e) {
    ElMessage.error(t('common.save_fail'))
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

const configRules = computed(() => ({
  regionName: [{ required: true, message: t('settings.enter_region'), trigger: 'blur' }],
  endpoint: [{ required: true, message: t('settings.enter_endpoint'), trigger: 'blur' }],
  projectId: [{ required: true, message: t('settings.enter_project_id'), trigger: 'blur' }],
  ak: [{ required: true, message: t('settings.enter_ak'), trigger: 'blur' }],
  sk: [{ required: true, message: t('settings.enter_sk'), trigger: 'blur' }],
}))

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
    ElMessage.error(t('common.fetch_fail'))
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
      ElMessage.success(isEditConfig.value ? t('common.update_success') : t('common.add_success'))
      configDialogVisible.value = false
      loadConfigList()
    } else {
      ElMessage.error(res.message || t('common.operation_fail'))
    }
  } catch (e) {
    ElMessage.error(t('common.operation_fail'))
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
      ElMessage.success(t('common.delete_success'))
      loadConfigList()
    } else {
      ElMessage.error(res.message || t('common.delete_fail'))
    }
  } catch (e) {
    ElMessage.error(t('common.delete_fail'))
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
      ElMessage.success(t('common.refresh_started'))
    } else {
      ElMessage.error(res.message || t('common.refresh_fail'))
    }
  } catch (e) {
    ElMessage.error(t('common.refresh_fail'))
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
