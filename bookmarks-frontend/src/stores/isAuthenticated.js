import { defineStore } from "pinia";
import { ref } from "vue"

export const authTokenStore = defineStore('authToken', () => {
    const token = ref("")

    function saveAuthToken(token) {
    if(localStorage.getItem('authToken') === undefined){
        this.token = token;
        localStorage.setItem('authToken', token);
        } else {
            return localStorage.getItem('authToken');
        }
    }

    return { token, saveAuthToken }
})