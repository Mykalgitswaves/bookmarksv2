<template>
  <div class="pt-5">
    <ul v-for="range in ranges" :key="range">
      <li
        @click="addBook(1)"
        class="flex flex-row gap-5 py-4 px-4 place-content-start bg-gray-100 rounded-md my-1 hover:bg-gray-200 max-w-[700px]"
      >
        <img class="h-24" src="../../assets/InfiniteJest.png" />
        <div class="flex flex-col justify-center">
          <p class="text-xl font-semibold text-gray-800">Infinite Jest</p>
          <p class="text-sm text-gray-800">David Foster Wallace</p>
          <span class="text-sm text-gray-500">February 1, 1996</span>
        </div>
      </li>
    </ul>
  </div>
</template>

<script>
import { useBookStore } from '../../stores/books'

export default {
  data() {
    return {
      dataRanges: [
        {
          pk: 1
        },
        {
          pk: 2
        },
        {
          pk: 3
        },
        {
          pk: 4
        },
        {
          pk: 5
        }
      ]
    }
  },
  methods: {
    addBook(book) {
      const state = useBookStore()
      state.addBook(book)
      console.log(state)
    }
  },
  computed: {
    ranges() {
      return this.dataRanges.slice(0, 3)
    }
  }
}
</script>
