<template>
  <div class="container grid grid-cols-1 relative px-5">
    <h2 class="text-3xl font-medium mb-4">What kind of reader are you?</h2>
    <p class="text-gray-500">Search for some of your favorite books</p>

    <form class="grid grid-cols-1 gap-2" action="submitForm" method="POST">
      <input
        class="py-2 px-4 rounded-md border-2 border-indigo-200 mt-5 w-62 max-w-[600px]"
        @change="searchBooks($event)"
        placeholder="Search for books"
        name="searchForBooks"
        type="text"
      />
      <label class="text-gray-600 text-sm" for="searchForBooks">
        Search for a book and tap to add it to your books
      </label>
    </form>

    <BookSearchResults class="max-w-[600px]" :data="data" />

    <button
      class="mt-5 px-20 py-3 bg-indigo-600 rounded-md text-indigo-100 max-w-[600px]"
      type="submit"
      @click.prevent="updateUser()"
    >
      Continue
    </button>
  </div>
</template>

<script>
import { createUserController } from '../../controllers/createuser';
import BookSearchResults from './booksearchresults.vue'
import { useStore } from '../../stores/page.js';
import { useBookStore } from '../../stores/books';
import { toRaw } from 'vue'

export default {
  components: {
    BookSearchResults
  },
  data() {
    return {
      formBlob: {},
      data: null,
      state: null
    }
  },
  methods: {
    async searchBooks(event) {
      try {
        const response = await fetch(`http://127.0.0.1:8000/books/${event.target.value}/`)
        const data = await response.json()
        this.data = data
        console.log(data)
      } catch (err) {
        console.log(err)
        this.data = null
      }
    },
    async updateUser() {
      const token = document.cookie;
      const books = toRaw(this.bookState.books)
      console.log(books)
      if(token && books) {
      try {
        await fetch('http://127.0.0.1:8000/setup-reader/books', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
          },
          body: JSON.stringify(books)
        })
        } catch(err) {
        console.log(err)
        }
      }
    },
    navigate() {
      this.state.getNextPage()
      console.log(this.state.page)
    }
  },
  mounted() {
    this.state = useStore()
    this.bookState = useBookStore()
  }
}
</script>
