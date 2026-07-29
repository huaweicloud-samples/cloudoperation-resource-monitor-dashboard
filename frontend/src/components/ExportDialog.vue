<template>
  <div class="export-dialog">
    <el-dialog v-model="visible" :title="$t('export_dialog.title')" width="480px" :before-close="handleClose" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item :label="$t('export_dialog.time_range')" prop="dateRange">
          <el-date-picker
            v-model="form.dateRange"
            type="daterange"
            :range-separator="$t('common.to')"
            :start-placeholder="$t('server_detail.start_date')"
            :end-placeholder="$t('server_detail.end_date')"
            value-format="YYYY-MM-DD"
            :disabled-date="disabledDate"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="handleClose">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="handleConfirm" :loading="loading">{{ $t('export_dialog.confirm_export') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'
import { exportCloudVmReport } from '@/api/cloudVm'

const props = defineProps({
  searchParams: { type: Object, default: () => ({}) },
  currentList: { type: Array, default: () => [] }
})

const emit = defineEmits(['success'])

const { t } = useI18n()

const visible = ref(false)
const loading = ref(false)
const formRef = ref(null)

const form = reactive({
  dateRange: []
})

const rules = computed(() => ({
  dateRange: [{ required: true, message: t('export_dialog.select_time_range'), trigger: 'change' }]
}))

const disabledDate = (time) => {
  return time.getTime() > Date.now()
}

function open() {
  visible.value = true
  form.dateRange = []
}

function handleClose() {
  visible.value = false
  formRef.value?.resetFields()
}

async function handleConfirm() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const params = {
      startDate: form.dateRange[0],
      endDate: form.dateRange[1],
      ...props.searchParams
    }
    await exportCloudVmReport(params, props.currentList)
    ElMessage.success(t('common.export_success'))
    emit('success')
    handleClose()
  } catch (e) {
    ElMessage.error(t('common.export_fail'))
  } finally {
    loading.value = false
  }
}

defineExpose({ open })
</script>