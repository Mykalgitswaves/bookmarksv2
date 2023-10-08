<template>
  <div class="px-4 pt-5">
    <KeepAlive>
      <ul 
        v-for="book in books" 
        :key="book.id"
      >
        <li
          @click="bookClickHandler(book);"
          :class="'flex flex-row gap-5 py-4 px-4 place-content-start bg-gray-100 rounded-md my-3 hover:bg-gray-200 max-w-[700px]' +
            (isToggled[book.id] === true ? 'border-solid border-indigo-200 border-2 bg-indigo-50' : '')"
        >
          <img class="h-24" :src="book.small_img_url" />
          <div class="flex flex-col justify-center">
            <p class="text-xl font-semibold text-gray-800">{{ book.title }}</p>
            
            <p v-for="name in book.author_names" :key="name" class="inline text-sm text-gray-800">{{ name }}</p>
            <span class="text-sm text-gray-500">{{ book.publication_year }}</span>
          </div>
        </li>

        <div class="inline-block my-1" v-if="isToggled[book.id] && !props.isAuth">
          <ul>
            <li v-for="index in reviewRange" :key="index" 
              class="inline-block"
            >
            
              <button type="button" :alt="index + ' score'" 
                @click="addScore({'score': index, 'book': book.id, 'book_title': book.title, 'book_authors': book.author_names, 'book_small_img_url': book.small_img_url})"
              >
                <Star v-bind="$attrs"
                  :isFilled="(bookScore.get(book.id) >= index ? true : false)"
                  class="mx-2 text-indigo-600 fill-indigo-600"
                />
              </button>
            </li>
          </ul>
        </div>
      </ul>
    </KeepAlive>
  </div>
</template>

<script setup>
import { useBookStore } from '../../stores/books'
import { toRaw, ref, computed, onMounted, defineProps, watch, defineEmits } from 'vue'
import Star from '../svg/icon-star.vue'

const promiseBooks = ref(null)
const fulfilledBooks = ref([])
const isToggled = ref({})
const bookScore = new Map()
const reviewRange = ref(5)

  const props = defineProps({
    data: {
      type: Array,
      required: true
    },
    isAuth: {
      type: Boolean,
      required: false,
      default: false
    },
    isComparison: {
      type: Boolean,
      required: false,
      default: false,
    }
  })
  const emit = defineEmits();

  const books = computed(() => (props.data));

  

  function addScore(object){
    // set to map obj cause its better ds for this.
    bookScore.set(object['book'], object['score'])
    // add raw object to state
    const state = useBookStore()
    const included = state.getBooks.filter(book => book.id === object['book'])
    if(included < 1){
      state.addBook({
        'id': object['book'], 
        'review': object['score'],
        'title': object['book_title'],
        'authors': object['book_authors'],
        'img_url': object['book_small_img_url']
      })
      state.saveStateToLocalStorage();
    }
  }
   
  function authEmit(book) {
    if(props.isAuth) {
      return emit('book-id', book)
    }
    return;
  }

  function bookClickHandler(book) {
    isToggled[book.id] = !isToggled[book.id];
    authEmit(book);
    isToggled.value[book.id] = true
    // if (props.isComparison) {
    //   const index = books.value.indexOf(book);
    //   comparator = [books.value[index]];
    // }
  }

  

  onMounted(() => {
    const state = useBookStore()
    const localStore = state.loadStateFromLocalStorage()
    if(localStore) {
      localStore.books.forEach(book => {
        isToggled.value[book.id] = true;
        // DO this for the rating
      })
    }
  })
</script>
