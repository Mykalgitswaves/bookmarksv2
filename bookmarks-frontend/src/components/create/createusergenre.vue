<template>
  <h2 class="text-3xl font-medium mb-4">What are some of your favorite genres?</h2>
  <p class="text-gray-500">Tap on your favorite genres</p>

  <input
    class="py-2 px-4 rounded-md border-2 border-indigo-200 mt-5 w-62 max-w-[600px]"
    @change="searchGenres($event)"
    placeholder="Search for genres"
    name="searchForBooks"
    type="text"
  />

  <div class="container mt-20 mb-36">
    <ul class="grid-pills justify-content-center">
      <li
        @click="addGenre(genre)"
        v-for="genre in genres"
        :key="genre"
        class="bg-gray-100 px-2 text-center py-2 rounded-lg border-2 border-solid border-gray-300 hover:border-indigo-500 text-lg"
      >
        <span>{{ genre }}</span>
      </li>
    </ul>
  </div>
  <button
    class="px-36 py-3 bg-indigo-600 rounded-md text-indigo-100"
    type="submit"
    @click="navigate"
  >
    Continue
  </button>
</template>

<script>
import { useStore } from '../../stores/page'
import { useBookStore } from '../../stores/books'

export default {
  data() {
    return {
      genres: ['English', 'Romance', 'Mystery', 'Horror', 'Cooking', 'Graphic Novels'],
      state: null
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
      console.log(state)
    },
    async searchGenres(event){
      try {
        const response = await fetch(`http://127.0.0.1:8000/genres/${event.target.value}`);
        const data = await response.json()
        console.log(data)
      } catch(err) {
        console.log(err)
      }
    }
  },
  mounted() {
    this.state = useStore()
  }
}
</script>
