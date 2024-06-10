import './assets/main.css'
import { createApp } from 'vue';
import { createPinia } from 'pinia';

import { directives } from './directives.js';
import App from './App.vue'
import router from './router'
export const app = createApp(App)
export const pinia = createPinia()
export const baseURL = import.meta.env.VUE_APP_BASE_URL;


app.config.productionTip = false;

directives.forEach((directive) => {
    app.directive(directive.name, directive.fn);
});

app.use(pinia);
app.use(router);
app.mount('#app');

export const app_router = router 

