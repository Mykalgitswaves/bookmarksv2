<template>
  <div class="px-4 pt-5">
    <ul v-for="book in data" :key="book.id">
      <li
        @click="
          addBook(book.id);
          isToggled[book.id] = !isToggled[book.id];
        "
        :class="
          'flex flex-row gap-5 py-4 px-4 place-content-start bg-gray-100 rounded-md my-1 hover:bg-gray-200 max-w-[700px]' +
          (isToggled[book.id] === true
            ? 'border-solid border-indigo-200 border-2 bg-indigo-50'
            : '')
        "
      >
        <img class="h-24" :src="book.small_img_url" />
        <div class="flex flex-col justify-center">
          <p class="text-xl font-semibold text-gray-800">{{ book.title }}</p>
          <p v-for="name in book.author_names" :key="name" class="inline text-sm text-gray-800">
            {{ name }}
          </p>
          <span class="text-sm text-gray-500">{{ book.publication_year }}</span>
        </div>
      </li>
      <div class="inline-block my-3" v-if="isToggled[book.id]">
        <p class="text-sm mb-3">review this book from worst to best (1 -> 5)</p>
        <ul>
          <li 
            v-for="index in reviewRange" 
            :key="index" 
            class="inline-block"
            @click="addScore({'score': index, 'book': book.id})"
          >
            
            <button :class="['px-3 py-2 mx-2 h-auto w-auto rounded-md border-solid border-2 border-indigo-600 text-indigo-500', 
              (getScore(book.id) >= index ? 'bg-indigo-600 text-base text-gray-100' : 'border-indigo-600' )]
            ">
              {{ index }}
            </button>
          </li>
        </ul>
      </div>
    </ul>
  </div>
</template>

<script>
import { useBookStore } from '../../stores/books'
import { toRaw } from 'vue'

export default {
  data() {
    return {
      promiseBooks: null,
      fulfilledBooks: [],
      isToggled: {},
      bookScore: new Map(),
      reviewRange: 5
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
      console.log(toRaw(state))
      console.log(this.isToggled)
    },
    addScore(object){
      // set to map obj cause its better ds for this.
      this.bookScore.set(object['book'], object['score'])
      // add raw object to state
      const state = useBookStore()
      state.addBook({'book': object['book'], 'review': object['score']})
      console.log(toRaw(state))
    },
    getScore(book) {
      return this.bookScore.get(book)
    }
  },
  mounted() {},
  computed: {}
}
</script>
