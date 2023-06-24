<template>
  <div class="container mx-auto grid grid-cols-1 justify-items-center">
    <h1 class="text-3xl font-semibold text-gray-900 mb-4">
      Who are some of your<br />
      favorite authors?
    </h1>
    <p class="text-gray-500">Search for some of your favorite authors</p>

    <input
      class="py-2 px-4 rounded-md border-2 border-indigo-200 mt-10 w-80 max-w-[600px]"
      @change="searchAuthors($event)"
      placeholder="Search for authors"
      name="searchForAuthor"
      type="text"
    />

    <AuthorSearch :authors="data" @author-data-updated="getAuthorData" />

    <RouterLink to="/home/">
      <button
        class="mt-5 px-28 py-3 bg-indigo-600 rounded-md text-indigo-100"
        type="submit"
        @click="finalizeUser"
      >
        Go to bookshelf
      </button>
    </RouterLink>
  </div>
</template>

<script>
import { useBookStore } from '../../stores/books'

import AuthorSearch from './authorSearch.vue'
import { finalizeUserController } from '../../controllers/createuser'
import { toRaw } from 'vue'

export default {
  components: {
    AuthorSearch
  },
  data() {
    const store = useBookStore()
    return {
      data: null,
      authors: [],
      store
    }
  },
  methods: {
    async searchAuthors(event) {
      try {
        const response = await fetch(`http://127.0.0.1:8000/authors/${event.target.value}/`)
        const data = await response.json()
        this.data = data
        console.log(data)
      } catch (err) {
        console.log(err)
        this.data = null
      }
    },
    getAuthorData(data) {
      console.log(data)
      const state = useBookStore();
      const id = parseInt(data[0])
      const name = data[1]
      const author = {
        id: id, 
        name: name
      }
      console.log(author)
      state.addAuthor(author)
    },
    async finalizeUser() {
      const state = useBookStore();
      console.log("this is a store", toRaw(state))
      const data = toRaw({books: state.books, genres: state.genres, authors: state.authors})
      // remember to take this out
      console.log(data)
      const response = await finalizeUserController.decorateUser(data)
      return response
    }
  },
  mounted() {}
}
</script>
