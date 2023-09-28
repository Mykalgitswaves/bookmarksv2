<template>
  <div class="max-w-[600px] px-5">
    <h2 class="text-3xl font-medium mb-4">What are some of your favorite genres?</h2>
    <p class="text-gray-500">Tap on your favorite genres</p>

    <input
      class="py-2 px-4 rounded-md border-2 border-indigo-200 mt-5 w-[100%]"
      v-bind="isEmpty"
      @keyup="searchGenres($event)"
      placeholder="Search for genres"
      name="searchForBooks"
      type="text"
    />

    <div v-if="genres !== null">
      <div class="w-60 container mt-5 mb-5 grid-pills justify-content-center">
        <div
          @click="addGenre(genre)"
          v-for="genre in genres"
          :key="genre"
          :class="
            isEmpty === false
              ? 'bg-gray-100 px-2 text-center py-2 rounded-lg border-2 border-solid border-gray-300 hover:border-indigo-500 text-lg'
              : ''
          "
        >
          {{ genre.name }}
        </div>
      </div>
    </div>
    <button
      class="block mt-5 px-20 py-3 bg-indigo-600 rounded-md text-indigo-100 w-[100%]"
      type="submit"
      @click.prevent="navigate(); updateGenres()"
    >
      Continue
    </button>
  </div>
</template>

<script>
import { useStore } from '../../stores/page'
import { useBookStore } from '../../stores/books'
import { toRaw } from 'vue'
import { helpersCtrl } from '../../services/helpers'

export default {
  data() {
    return {
      genres: null,
      addedGenre: [],
      state: null,
      isEmpty: ''
    }
  },
  watch: {
    genres: {
      handler(newValue) {
        console.log(newValue)
        if (!newValue.length) {
          this.isEmpty = true
        }
      }
    }
  },
  methods: {
    navigate() {
      this.state.getNextPage()
      console.log(this.state.page)
    },
    addGenre(genre) {
      const state = useBookStore()
      state.addGenre(genre)
      this.addedGenre.push(genre)
      console.log(toRaw(state))
    },
    async searchGenres(event) {
      try {
        const response = await fetch(`http://127.0.0.1:8000/genres/${event.target.value}`)
        const data = await response.json()
        if (data.detail !== 'Not found') {
          this.genres = data
          this.isEmpty = false
          console.log(data)
        }
      } catch (err) {
        console.log(err)
        this.isEmpty = true
      }
    },
    async updateGenres() {
      const token = helpersCtrl.getCookieByParam(['token']);
      const genreStore = useBookStore();
      const genres = toRaw(genreStore.genres);
      
      if(token && genres) {
        try {
          await fetch('http://127.0.0.1:8000/setup-reader/genres', {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${token}`
            },
            body: JSON.stringify(genres)
          })
        } catch(err) {
          console.log(err)
        }
      }
    }
  },
  mounted() {
    this.state = useStore()
  }
}
</script>
