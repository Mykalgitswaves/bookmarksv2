<template>
  <div class="px-4 pt-5">
    <ul v-for="(book, index) in data" :key="index">
      <li
        @click="addBook(1)"
        class="flex flex-row gap-5 py-4 px-4 place-content-start bg-gray-100 rounded-md my-1 hover:bg-gray-200 max-w-[700px]"
      >
        <img class="h-24" :src="book.small_img_url" />
        <div class="flex flex-col justify-center">
          <p class="text-xl font-semibold text-gray-800">{{ book.title }}</p>
          <p v-for="name in book.author_names" :key="name"
            class="text-sm text-gray-800">{{ name }}</p>
          <span class="text-sm text-gray-500">{{ book.publication_year }}</span>
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
      ],
      promiseBooks: null,
      fulfilledBooks: []
    }
  },
  props: {
    data: {
      type: Array,
      required: true
    }
  },
  methods: {
    addBook(book) {
      const state = useBookStore()
      state.addBook(book)
      console.log(state)
    },
    async fetchBooks() {
      try {
        const response = await fetch('http://127.0.0.1:8000/books')
        this.promiseBooks = await response.json()
      } catch(err) {
        console.log(err);
      }
    }
  },
  mounted(){
    // this.fetchBooks()
  },
  computed: {
  }
}
</script>
