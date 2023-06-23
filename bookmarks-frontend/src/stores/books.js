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
    loadBooks() {
      const state = localStorage.getItem('bookStore')
      this.books = state.books
    },
    removeBook(book) {
      const index = this.books.findIndex((b) => b.pk === book.pk)
      if (index !== -1) {
        this.books.splice(index, 1)
        this.saveStateToLocalStorage()
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
    loadStateFromLocalStorage() {
      const state = localStorage.getItem('bookStore')
      return state
    }
  },
  created() {
    this.loadStateFromLocalStorage()
  }
})
