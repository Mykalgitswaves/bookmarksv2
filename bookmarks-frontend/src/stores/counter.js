import { defineStore } from 'pinia';

export const useStore = defineStore('formState', {
  state: () => ({ page: 1}),
  actions: {
    getNextPage(){
      
        this.page++
    },
    getPrevPage(){
      this.page--
    }
  }
})
