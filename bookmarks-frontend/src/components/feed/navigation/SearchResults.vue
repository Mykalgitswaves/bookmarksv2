<template>
    <div class="container w-[100%] h-auto" v-if="store.data">
        <div class="flex flex-col justify-between items-center w-100 ">
            <div class="mb-2 flex flex-col">
                <p class="text-indigo-500 mb-2">
                    Authors {{ authors.length }}
                </p>
                
                <button
                    v-for="(author, index) in authors"
                    :key="index"
                    class="searchbar-item"
                    @click="toAuthorPage(author)"
                >
                    {{ author.name }}
                </button>
            </div>
        </div>
        
        <div>
            <button
                class="text-slate-500"
                @click="ivFn(books, isViewBooks)"
            >
                <span :class="isInactiveClass(books)">
                    Books {{ books.length }}
                </span>
            </button>

            <ul v-if="isViewBooks && books.length">
                <li v-for="(book, index) in books" :key="index">
                    {{ book.name }}
                </li>
            </ul>
        </div>
    </div>
</template>

<script setup>
import { toRaw, computed, ref } from "vue"
import { useRouter, useRoute } from 'vue-router';
import { searchResultStore } from '@/stores/searchBar.js';
import { helpersCtrl } from '@/services/helpers.js'

const store = searchResultStore()
const data = ref(null)
data.value = store.data

const authors = computed(() => (store.data.authors ? store.data.authors : ['No authors for you']));
const books = computed(() => (store.data.books ? store.data.books : ['No books for you']));
const books_by_genre = computed(() => (store.data.books_by_genre ? store.data.books_by_genre : ['No books with that genre for you']));
const books_by_author = computed(() => (store.data.books_by_author ? store.data.books_by_author : ['No books by that author for you']));
const users = computed(() => (store.data.users ? store.data.users : ['No users for you']));

// stuff for routing
const router = useRouter();
const route = useRoute();
const user = route.params.user

function isInactiveClass(computedArray) {
    return 'font-medium ' + (computedArray.length ? 'text-indigo-500' : 'text-slate-500');
}

function toAuthorPage(author){
    return router.push(`/feed/${user}/authors/${author.id}`);
}

</script>

<style scoped>
.searchbar-item {
    text-align: start;
    display: flex;
    margin: .25rem 0;
    padding: .25rem 1rem;
    background-color: #fcf8ff;
    border-radius: 4px;
    width: 100%;
    transition: background 100ms ease-in;
    font-weight: 500;
}
.searchbar-item:hover {
    background-color: #f4e7fd;
    transition: background 100ms ease-in;
}
</style>