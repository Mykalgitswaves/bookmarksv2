import './assets/main.css'
import { createApp } from 'vue';
import { createPinia } from 'pinia';    1

import { directives } from './directives.js';
import App from './App.vue'
import router from './router'
export const app = createApp(App)
export const pinia = createPinia()
export const baseURL = import.meta.env.VUE_APP_BASE_URL;

// This will break if we change the name: TODO: @kylearbide make sure i don't break this.
const prodEnvHosts = 'https://hardcoverlit.com/'

app.config.productionTip = false;

directives.forEach((directive) => {
    app.directive(directive.name, directive.fn);
});

app.use(pinia);
app.use(router);
app.mount('#app');

// attach the vue app instance to the window so you can debug when developing locally.
if (window.location.origin !== prodEnvHosts) {
    window.$$v = app;
}

export const app_router = router 

