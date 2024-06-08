<template>
  <div class="container mx-auto grid grid-cols-1 justify-items-center">
    <h1 class="text-3xl font-semibold text-gray-900 mb-4">
      Who are some of your<br />
      favorite authors?
    </h1>
    <p class="text-gray-500">Search for some of your favorite authors</p>

    <input
      class="py-2 px-4 rounded-md border-2 border-indigo-200 mt-10 w-80 max-w-[600px]"
      @keyup="debouncedSearchAuthors($event)"
      placeholder="Search for authors"
      name="searchForAuthor"
      type="text"
    />

    <AuthorSearch :authors="data" @author-data-updated="getAuthorData" />

    
      <button
        class="mt-5 px-28 py-3 bg-indigo-600 rounded-md text-indigo-100"
        type="submit"
        @click.prevent="updateAuthors()"
      >
        Go to bookshelf
      </button>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useBookStore } from '../../stores/books';
import { useStore } from '../../stores/page';
import AuthorSearch from './authorSearch.vue';
import { app_router } from '@/main.js';
import { helpersCtrl } from '../../services/helpers';
import { urls } from '../../services/urls';

const { debounce } = helpersCtrl;
const store = useBookStore()

const data = ref(null);
const authors = ref([]);
  
async function searchAuthors(event) {
  try {
    if(event.target.value.length) {
    const response = await fetch(`http://127.0.0.1:8000/authors/${event.target.value}/`);
    const d = await response.json();
    data.value = d
    console.log(data)
    }
  } catch (err) {
    console.log(err)
    data.value = null
  }
}

const debouncedSearchAuthors = debounce(searchAuthors, 500, false);

function getAuthorData(data) {
  const state = useBookStore();
  const id = parseInt(data[0]);
  const name = data[1];
  const author = {
    id: id, 
    name: name
  }

  state.addAuthor(author);
}

async function updateAuthors() {
    const token = helpersCtrl.getCookieByParam(['token']);
    const store = useBookStore();
    const pageStore = useStore();
    let authors = store.getAuthorsIds
    if(token && authors) {
    try {
      await fetch('http://127.0.0.1:8000/setup-reader/authors/', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(authors)
      }).then((response) => {
        if (!response.ok) {
          throw new Error('Network response was not ok')
          }
        return response.json()
      }).then((data) => {
          app_router.push(`/feed/${data.uuid}/all`)
          store.createUserSuccess()
          pageStore.clearPageStore()
        })
      } catch(err) {
        console.log(err)
      }
    }
  }
</script>
