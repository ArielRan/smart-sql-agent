<template>
  <div style="padding:20px">
    <el-input v-model="question" placeholder="请输入问题" />
    <el-button type="primary" style="margin-top:10px" @click="submit">
      发送
    </el-button>

    <div v-if="result" style="margin-top:20px">
      <h3>SQL</h3>
      <pre>{{ result.sql }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { sendMessage } from '../api/chat'

const question = ref('')
const result = ref(null)

const submit = async () => {
  const res = await sendMessage(question.value)
  result.value = res.data
}
</script>