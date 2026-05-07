import axios from 'axios'

export function sendMessage(question) {
  return axios.post('/chat', {
    question
  })
}