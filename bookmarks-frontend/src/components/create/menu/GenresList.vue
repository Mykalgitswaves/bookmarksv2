<template>
    <div class="mx-10 mt-10 md:mx-52">
        <div class="mt-5 mb-5 grid-pills menu">
        <div
          @click="(genre.id !== 0 ? removeGenre(genre) : '')"
          v-for="genre in genres"
          :key="genre.id"
          class="border-indigo-300 text-indigo-900 bg-gray-100 px-2 text-center py-2 rounded-lg border-2 border-solid text-lg"
        >
          {{ genre.name }}
        </div>
      </div>
    </div>
</template>
<script setup>
import { useBookStore } from '@/stores/books.js';
import { useStore } from '@/stores/page.js';
import BookIcon from '../../svg/icon-book.vue';
import { computed } from 'vue';

const store = useBookStore();
store.loadStateFromLocalStorage();

const nullState = [{
    id: 0,
    name: 'None added'
}]

const genres = computed(() => ((store.getGenres.length > 0) ? store.getGenres : nullState))
console.log(store.genres)
</script>