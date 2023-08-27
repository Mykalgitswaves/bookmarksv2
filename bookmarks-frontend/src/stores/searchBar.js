import { defineStore } from 'pinia';
import {ref} from 'vue'

export const searchResultStore = defineStore('searchResults' , () => {
    
        const data = ref(null);
        function saveAndLoadSearchResults(newData) {
            // Check to see if there is data in storage or if ref is already not null
            if(this.data === null){
                // if not save new data store to data arg being passed in
               this.data = newData;
            } else {
                // otherwise set this data = to search data saved in local storage
                return this.data
            }
        }
    return { data, saveAndLoadSearchResults }
})