import './assets/main.css'

import { createApp } from 'vue';
import { createPinia } from 'pinia';
import JSConfetti from 'js-confetti';
// Not using any of these rn.
import './webcomponents/cts-sort-items.js';
import './webcomponents/sort-items.js';
import './webcomponents/webc-lib.js';

import { directives } from './directives.js';
import App from './App.vue'
import router from './router'
export const app = createApp(App)
export const pinia = createPinia()
export const baseURL = 'http://127.0.0.1:8000/';

app.config.ignoredElements = ['sort-item', 'cts-sort-item'];
app.config.productionTip = false;

directives.forEach((directive) => {
    app.directive(directive.name, directive.fn);
});

app.use(pinia);
app.use(router);
app.mount('#app');

console.log(app)
// const sortItemElement = defineCustomElement(SortItem);
// app.customElements.define('sort-item', SortItem);

export const app_router = router 

