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

    <BookSearchResults class="max-w-[600px]" :data="searchResultArray"/>
</template>
<script setup>
import { ref } from 'vue';
import BookSearchResults from '../../create/booksearchresults.vue';

const searchResultsArray = ref(null);

function searchBooks(e) {
    
}
</script>