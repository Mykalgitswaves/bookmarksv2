import './assets/main.css'

import { createApp } from 'vue';
import { createPinia } from 'pinia';

// For store of creating user data

import App from './App.vue'
import router from './router'
export const app = createApp(App)
export const pinia = createPinia()
export const baseURL = 'http://127.0.0.1:8000/';

app.use(pinia)
app.use(router)
app.mount('#app')

export const app_router = router 

