import { defineStore } from 'pinia'
// Todo persist state with local storage so people can leave page/refresh and not start over
export const useStore = defineStore('formState', {
  state: () => ({ page: 1 }),
  actions: {
    getNextPage() {
      
      // if(localStorage.getItem('page') === null || undefined) { 
      //   // for starters check if state is persisted in local storage
      //   // if not then save new state
        this.page++
      //   localStorage.setItem('page', this.page) 
      // } else {
      //   this.page = localStorage.getItem('page')
      //   this.page + 1      
      //   }
    },
    getPrevPage() {
      this.page--
    }
  }
})
