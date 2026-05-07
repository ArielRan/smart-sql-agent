<template>
  <div style="padding:20px; max-width:900px; margin:0 auto;">
    <h2>Smart SQL Agent</h2>

    <div style="display:flex; gap:10px;">
      <el-input
        v-model="question"
        placeholder="请输入问题，例如：系统有多少用户？"
        @keyup.enter="submit"
      />
      <el-button type="primary" @click="submit" :loading="loading">
        发送
      </el-button>
    </div>

    <div v-if="result" style="margin-top:24px;">
      <!-- 自然语言回复 -->
      <el-alert :title="result.answer" type="success" :closable="false" show-icon />

      <!-- 表格展示 -->
      <div v-if="result.display_type === 'table' && result.columns.length" style="margin-top:16px;">
        <el-table :data="result.data" border stripe max-height="500" style="width:100%">
          <el-table-column
            v-for="col in result.columns"
            :key="col"
            :prop="col"
            :label="col"
            min-width="120"
          />
        </el-table>
        <p style="color:#999; font-size:12px; margin-top:8px;">
          共 {{ result.data.length }} 条记录
        </p>
      </div>

      <!-- SQL 参考 -->
      <el-collapse style="margin-top:16px;">
        <el-collapse-item title="查看 SQL">
          <pre style="background:#f5f5f5; padding:12px; border-radius:4px; overflow-x:auto;">{{ result.sql }}</pre>
        </el-collapse-item>
      </el-collapse>
    </div>

    <el-empty v-if="!result && !loading" description="请输入问题开始查询" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { sendMessage } from '../api/chat'

const question = ref('')
const result = ref(null)
const loading = ref(false)

const submit = async () => {
  if (!question.value.trim()) return
  loading.value = true
  try {
    const res = await sendMessage(question.value)
    result.value = res.data
  } catch (e) {
    result.value = {
      answer: '请求失败: ' + (e.response?.data?.detail || e.message),
      display_type: 'text',
      columns: [],
      data: [],
      sql: '',
    }
  }
  loading.value = false
}
</script>
