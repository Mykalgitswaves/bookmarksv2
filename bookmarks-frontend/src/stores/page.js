import { defineStore } from 'pinia'
// Todo persist state with local storage so people can leave page/refresh and not start over
export const useStore = defineStore('formState', {
  state: () => ({
    page: parseInt(localStorage.getItem('page')) || 0 // Retrieve from local storage or default to 0
  }),
  actions: {
    getNextPage() {
      this.page++
      if (this.page > 4) {
        this.page = 4 // Restrict page value to a maximum of 4
      }
      localStorage.setItem('page', this.page.toString()) // Save updated page value to local storage
    },
    getPrevPage() {
      this.page--
      if (this.page < 0) {
        this.page = 0 // Restrict page value to a minimum of 0
      }
      localStorage.setItem('page', this.page.toString()) // Save updated page value to local storage
    }
  }
})
