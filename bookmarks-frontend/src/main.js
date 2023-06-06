import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
// For store of creating user data

import App from './App.vue'
import router from './router'

export const app = createApp(App)
export const pinia = createPinia()

app.use(pinia)
app.use(router)

app.mount('#app')
