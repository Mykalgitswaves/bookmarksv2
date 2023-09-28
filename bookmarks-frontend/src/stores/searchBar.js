import { defineStore } from 'pinia';
import { ref } from 'vue'

export const searchResultStore = defineStore('searchResults' , () => {
        const data = ref(null);
        function saveAndLoadSearchResults(newData) {
            data.value = newData;
            console.log(data.value, newData)
            return data.value
        }
    return { data, saveAndLoadSearchResults }
})