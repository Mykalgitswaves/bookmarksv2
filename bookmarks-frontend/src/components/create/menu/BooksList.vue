<template>
    <div class="h-[ 500px ] overflow-y-scroll mx-10 mt-10 md:mx-52">
        <ul >
            <li
                @click="(book.id === 0 ? goToBookSearchPage(): '')"
                v-for="book in books" 
                :key="book.id"
                class="max-h-[150px] w-[100%] flex flex-row gap-5 py-2 px-4 place-content-start bg-indigo-100 rounded-md my-3 hover:bg-gray-200"
            >
                <img
                    v-if="book.id !== 0"
                    class="h-24 aspect-ratio"
                    :src="book.img_url" 
                />

                <BookIcon v-else/>
                
                <div class="flex flex-col justify-center">
                    <p class="text-xl font-semibold text-gray-800">{{ book.title }}</p>
                    
                    <p v-for="name in book.author_names" :key="name" class="inline text-sm text-gray-800">{{ name }}</p>
                    <span class="text-sm text-gray-500">{{ book.publication_year }}</span>
                </div>
            </li>
        </ul>
    </div>
</template>
<script setup>
import { useBookStore } from '@/stores/books.js';
import { useStore } from '@/stores/page.js';
import BookIcon from '../../svg/icon-book.vue'
import { computed, toRaw } from 'vue'


let store = useBookStore()

const nullState = [{
    id: 0,
    title: 'No books added yet',
    author_names: ['Add books for a better recommendations'],
    publication_year: ''
}]

const books = computed(() => ((store.getBooks.length > 0) ? store.getBooks : nullState))
console.log(store.books)

function goToBookSearchPage() {
    const store = useStore();
    store.goToPage(2)
}

</script>