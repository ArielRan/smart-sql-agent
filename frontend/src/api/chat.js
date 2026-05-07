import axios from 'axios'

export function sendMessage(question) {
  return axios.post('http://127.0.0.1:8000/chat', {
    question
  })
}