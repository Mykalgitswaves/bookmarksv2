import { defineStore } from 'pinia'
import { toRaw } from 'vue'

export const useBookStore = defineStore('addBooks', {
  state: () => ({
    books: new Set(),
    genres: new Set(),
    authors: new Set()
  }),
  actions: {
    addBook(book) {
        this.books[book.id] = book
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
    removeBook(book) {
      if (this.books.has(book.id)) {
        this.books.delete(book.id)
        this.saveStateToLocalStorage()
      }
    },
    addGenre(genre) {
        this.genres[genre.id] = genre
        this.saveStateToLocalStorage()
    },
    addAuthor(author) {
        this.authors[author.id] = author
        this.saveStateToLocalStorage()
    },
    saveStateToLocalStorage() {
      const state = JSON.stringify(this.$state)
      localStorage.setItem('bookStore', state)
    },
    createUserSuccess() {
      this.genres = new Set;
      this.authors = new Set()
      this.books = new Set()
      localStorage.removeItem('bookStore');
    }
  },
  getters: {
    getBooks(){
      this.loadStateFromLocalStorage()
      let arr = []
      if(this.$state){
        const rawBooks = toRaw(this.books)
        for (let key in rawBooks){
          arr.push(rawBooks[key])
        }
      }
      return arr
    },
    getGenres() {
      this.loadStateFromLocalStorage()
      let arr = []
      if(this.$state){
        const rawGenres = toRaw(this.genres)
        for(let key in rawGenres) {
          arr.push(rawGenres[key])
        }
      }
      return arr
    },
    getAuthors() {
      this.loadStateFromLocalStorage()
      let arr = []
      if(this.$state){
        const rawAuthors = toRaw(this.authors)
        for(let key in rawAuthors) {
          arr.push(rawAuthors[key])
        }
      }
      return arr
    },
    getAuthorsIds() {
      this.loadStateFromLocalStorage()
      let arr = []
      if(this.$state){
        const rawAuthors = toRaw(this.authors)
        for(let key in rawAuthors) {
          arr.push(rawAuthors[key].id)
        }
      }
      console.log(`id array for authors: ${arr}`)
      return arr
    }
  },
  created() {
    this.loadStateFromLocalStorage()
  }
})
