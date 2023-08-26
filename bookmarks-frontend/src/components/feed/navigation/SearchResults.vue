<template>
    <div class="container">
        <h1>Search Results</h1>  
        <div class="flex justify-between items-center">
            <button
                class="text-slate-500"
                @click="ivFn(authors. isViewAuthors)"
            >
                <span :class="isInactiveClass(authors)">
                    Authors {{ authors.length }}
                </span>
            </button>
            <button
                class="text-slate-500"
                @click="ivFn(books, isViewBooks)"
            >
                <span :class="isInactiveClass(books)">
                    Books {{ books.length }}
                </span>
            </button>
        </div>
        <ul v-if="isViewAuthors">
            <li v-for="(author, index) in authors" :key="index">
                {{ author.name }}
            </li>
        </ul>
        <ul v-if="isViewBooks">
            <li v-for="(book, index) in books" :key="index">
                {{ book.name }}
            </li>
        </ul>
        
    </div>
</template>

<script setup>
import { toRaw, computed, ref } from "vue"
import { useStore } from '@/stores/searchBar.js';

const searchResultStore = useStore()
const rawData = searchResultStore.data
const data = toRaw(rawData);

const authors = computed(() => (data.authors));
const books = computed(() => (data.books));
const books_by_genre = computed(() => (data.books_by_genre));
const books_by_author = computed(() => (data.books_by_author));
const users = computed(() => (data.users.length ? data.users : ['No users with that']));

const isViewAuthors = ref(false) ;
const isViewBooks = ref(false);

function ivFn(computedArray, computedBoolean){
    if(computedArray.value.length > 0) {
        computedBoolean.value = !computedBoolean.value;
    }
    return;
}

function isInactiveClass(computedArray) {
    return 'font-semibold ' + (computedArray.value.length ? 'text-indigo-500' : 'text-slate-500');
}

</script>