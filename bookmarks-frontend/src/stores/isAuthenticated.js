import { defineStore } from "pinia";
import { ref, toRaw } from "vue"

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
    function getAuthToken() {
        this.token = localStorage.getItem('authToken')
        console.log(toRaw(JSON.parse(this.token)))
        return toRaw(JSON.parse(this.token));
    }

    return { token, saveAuthToken }
})