import './assets/main.css'

import { createApp } from 'vue';
import { createPinia } from 'pinia';

import './webcomponents/sort-items.js';
import './webcomponents/webc-lib.js';
// For store of creating user data

import App from './App.vue'
import router from './router'
export const app = createApp(App)
export const pinia = createPinia()
export const baseURL = 'http://127.0.0.1:8000/';
app.config.ignoredElements = ['sort-item'];
app.config.productionTip = false

app.use(pinia);
app.use(router);
app.mount('#app');
console.log(app)
// const sortItemElement = defineCustomElement(SortItem);
// app.customElements.define('sort-item', SortItem);

export const app_router = router 

