import { defineStore } from 'pinia'
import {ref} from 'vue'

export const useNavigationStore = defineStore('navbar', () => {
    const navState = ref(0)
    return { navState }
})