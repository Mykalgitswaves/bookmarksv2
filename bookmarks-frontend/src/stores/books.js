import { defineStore } from 'pinia'

export const useBookStore = defineStore('addBooks', {
  state: () => ({
    books: [],
    genres: [],
    authors: []
  }),
  actions: {
    addBook(book) {
      this.books.push(book)
      this.saveStateToLocalStorage()
    },
    loadStateFromLocalStorage() {
        // const authState = authTokenStore()
          const state = JSON.parse(localStorage.getItem('bookStore'))
          if(state) {
            console.log(state)
            this.books = state.books
            this.genres = state.genres
            this.authors = state.authors
          }
    },
    getBooks(){
      this.loadStateFromLocalStorage()
      return this.books
    },
    getGenres() {
      this.loadStateFromLocalStorage()
      return this.genres
    },
    getAuthors() {
      this.loadStateFromLocalStorage()
      return this.authors
    },
    removeBook(book) {
      const index = this.books.findIndex((b) => b.pk === book.pk)
      if (index !== -1) {
        this.books.splice(index, index + 1)
        this.saveStateToLocalStorage()
        return this.books
      }
    },
    addGenre(genre) {
      if (!this.genres.includes(genre)) {
        this.genres.push(genre)
        this.saveStateToLocalStorage()
      }
    },
    addAuthor(author) {
      this.authors.push(author)
      this.saveStateToLocalStorage()
    },
    saveStateToLocalStorage() {
      const state = JSON.stringify(this.$state)
      localStorage.setItem('bookStore', state)
    },
  },
  created() {
    this.loadState()
  }
})
