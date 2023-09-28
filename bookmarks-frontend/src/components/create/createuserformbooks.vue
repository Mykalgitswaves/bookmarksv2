<template>
  <div class="container grid grid-cols-1 relative px-5">
    <h2 class="text-3xl font-medium mb-4">What kind of reader are you?</h2>
    <p class="text-gray-500">Search for some of your favorite books</p>

    <div class="grid grid-cols-1 gap-2">
      <input
        class="py-2 px-4 rounded-md border-2 border-indigo-200 mt-5 w-62 max-w-[600px]"
        @keyup="searchBooks($event)"
        placeholder="Search for books"
        name="searchForBooks"
        type="text"
      />

      <label class="text-gray-600 text-sm" for="searchForBooks">
        Tap a book and review it to add it to your shelf
      </label>
    </div>

    <BookSearchResults class="max-w-[600px]" :data="searchResultArray"/>
    
    <button
      class=" mt-5 px-20 py-3 bg-indigo-600 rounded-md text-indigo-100 w-88 max-w-[600px]"
      type="submit"
      @click.prevent="updateUser(); navigate()"
    >
      Continue
    </button>
  </div>
</template>

<script setup>
import { toRaw, ref, computed } from 'vue'
import BookSearchResults from './booksearchresults.vue'
import { useStore } from '../../stores/page.js';
import { useBookStore } from '../../stores/books';
import { helpersCtrl } from '../../services/helpers';
    
const formBlob = ref({});
const dataRef = ref([]);
const state = ref(null);

const searchResultArray = computed(() => (dataRef.value))

const bookState = useBookStore()

function navigate() {
  const store = useStore();
  store.getNextPage();
  console.log(store.page);
}

async function searchBooks(event) {
  try {
    const response = await fetch(`http://127.0.0.1:8000/books/${event.target.value}/`)
    const data = await response.json()
    dataRef.value = data.data
    console.log(data.value, 'this data')
  } catch (err) {
    console.log(err)
  }
}

async function updateUser() {
  const token = helpersCtrl.getCookieByParam('token');
  const books = toRaw(bookState.books)
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
}

</script>
