<template>
  <div class="export-dialog">
    <el-dialog v-model="visible" title="导出报告" width="480px" :before-close="handleClose" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="时间段" prop="dateRange">
          <el-date-picker
            v-model="form.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            :disabled-date="disabledDate"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleConfirm" :loading="loading">确认导出</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { exportCloudVmReport } from '@/api/cloudVm'

const props = defineProps({
  searchParams: { type: Object, default: () => ({}) },
  currentList: { type: Array, default: () => [] }
})

const emit = defineEmits(['success'])

const visible = ref(false)
const loading = ref(false)
const formRef = ref(null)

const form = reactive({
  dateRange: []
})

const rules = {
  dateRange: [{ required: true, message: '请选择时间段', trigger: 'change' }]
}

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
    ElMessage.success('导出成功')
    emit('success')
    handleClose()
  } catch (e) {
    ElMessage.error('导出失败')
  } finally {
    loading.value = false
  }
}

defineExpose({ open })
</script>