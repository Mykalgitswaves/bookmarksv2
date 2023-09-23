<template>
     <form class="grid grid-cols-1 gap-2" action="submitForm" method="POST">
      <input
        class="py-2 px-4 rounded-md border-2 border-indigo-200 mt-5 w-62 max-w-[600px]"
        @change="searchBooks($event)"
        placeholder="Search for books"
        name="searchForBooks"
        type="text"
      />
      <label class="text-gray-600 text-sm" for="searchForBooks">
        Tap a book and review it to add it to your shelf
      </label>
    </form>

    <BookSearchResults class="max-w-[600px]" :data="books" :is-auth="true" @book-id="toParent"/>
</template>
<script setup>
import { ref, computed, defineEmits } from 'vue';
import BookSearchResults from '../../create/booksearchresults.vue';
import { db } from '../../../services/db';
import { urls } from '../../../services/urls';

const emit = defineEmits()
const searchResultsArray = ref(null);

async function searchBooks(e) {
  searchResultsArray.value = await db.get(urls.setup.bookByText(e.target.value))
  console.log(searchResultsArray.value, 'logging this shit boy')
}

function toParent(e) {
  emit('book-to-parent', e)
}

const books = computed(() => (searchResultsArray.value && searchResultsArray.value.data ? searchResultsArray.value.data : ''))



</script>