<template>
    <div class="mx-10 mt-10 md:mx-52">
        <ul>
      <li
        v-for="author in authors"
        :key="author.id"
        class="flex flex-row gap-5 py-4 px-4 place-content-start
        bg-indigo-50 rounded-md hover:bg-gray-200 border-solid
        border-indigo-200 border-2 my-5"
      >
        <div class="flex flex-col justify-center">
          <p class="text-xl font-semibold text-gray-800">{{ author.name }}</p>
          <p v-if="author.author_description" class="text-gray-500">{{ author.author_description }}</p>
        </div>
      </li>
    </ul>
    </div>
</template>
<script setup>
import { useBookStore } from '@/stores/books.js';
import { useStore } from '@/stores/page.js';
import { computed } from 'vue'

const store = useBookStore()
store.loadStateFromLocalStorage()

const nullState = [{
    id: 0,
    name: 'No authors added',
    author_description: 'Add your favorite writers for better recommendations',
}]

const authors = computed(() => ((store.getAuthors.length > 0) ? store.getAuthors : nullState))
console.log(authors, 'cashmoneyyyyy')

</script>