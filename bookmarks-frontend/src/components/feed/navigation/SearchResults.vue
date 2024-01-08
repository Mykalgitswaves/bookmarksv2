<template>
    <div class="h-auto flex-col gap-5 mt-10" v-if="store.data">
        <div v-if="f['authors'] && authors?.length > 0">
            <div class="mb-2 flex flex-col">
                <p class="text-slate-600 text-lg mb-2">
                    <span class="text-indigo-500 text-2xl mr-2">{{ authors.length }}</span> Authors
                </p>
                <div class="author-row">
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
        </div>

        <div v-if="f['users'] && users?.length > 0" class="my-5">
            <p class="text-slate-600 text-lg mb-2">
                <span class="text-indigo-500 text-2xl mr-2 ">{{ users.length }}</span> Users
            </p>
            <div class="author-row">
                <button 
                    v-for="(user, index) in users" 
                    :key="index"
                    class="searchbar-item"
                    @click="toUserPage(user)"
                >
                    {{ user }}
                </button>            
            </div>
        </div>
        
        <div v-if="f['books'] && books?.length > 0">
            <p class="text-slate-600 text-lg mb-2">
                <span class="text-indigo-500 text-2xl mr-2">{{ books.length }}</span>
                Books
            </p>

            <div class="searchbar-row">
                <button 
                    v-for="(book, index) in books" 
                    :key="index"
                    class="searchbar-item"
                    @click="toBookPage(book)"
                >   
                    <span>
                        <div>
                            <img
                                class="px-2 py-2 rounded-md hover:bg-slate-400" 
                                :src="book.img_url" 
                                :alt="book.title + ' image'"/>
                            <span class="ml-2 searchbar-title text-indigo-900">{{ book.title }}</span>
                        </div>
                    </span>
                </button>            
            </div>
        </div>

        <div v-if="f['genres']&& books_by_genre?.length > 0">
            <p class="text-indigo-500 mb-2">
                Books by genre {{ books_by_genre.length }}
            </p>

            <button 
                v-for="(book, index) in books_by_genre" 
                :key="index"
                class="searchbar-item"
                @click="toBookPage(book)"
            >
                {{ book.title }}
            </button>            
        </div>

        <div v-if="f['books_by_author'] && books_by_author?.length > 0">
            <p class="text-indigo-500 mb-2">
                Books by author {{ books_by_author.length }}
            </p>

            <button 
                v-for="(book, index) in books_by_author" 
                :key="index"
                class="searchbar-item"
                @click="toBookPage(book)"
            >
                {{ book.title }}
            </button>            
        </div>
    </div>
</template>

<script setup>
import { toRefs, computed, ref, reactive, watch } from "vue"
import { useRouter, useRoute } from 'vue-router';
import { searchResultStore } from '@/stores/searchBar.js';

const props = defineProps({
    newData: {
        type: Object,
    },
    filters: {
        type: Object,
    }
})

const f = ref({
    "authors": true,
    "users": true,
    "books": true,
    "genres": true,
    "books_by_author": true,
    "reset": false
});

const { newData, filters } = toRefs(props) 

const store = searchResultStore()
const data = ref(null);

data.value = newData.value;

const authors = computed(() => (store.data.authors ? store.data.authors : ['No authors for you']));
const books = computed(() => (store.data.books ? store.data.books : ['No books for you']));
const books_by_genre = computed(() => (store.data.books_by_genre ? store.data.books_by_genre : ['No books with that genre for you']));
const books_by_author = computed(() => (store.data.books_by_author ? store.data.books_by_author : ['No books by that author for you']));
const users = computed(() => (store.data.users ? store.data.users : ['No users for you']));

// stuff for routing
const router = useRouter();
const route = useRoute();
const user = route.params.user

function toAuthorPage(author){
    return router.push(`/feed/${user}/authors/${author.id}`);
}

function toBookPage(book){
    return router.push(`/feed/${user}/works/${book.id}`)
}

function toUserPage(user_id){
    return router.push(`/feed/${user}/users/${user_id}`);
}


function resetFilters() {
    const keys = Array.from(Object.keys(f.value))
    keys.forEach((key) => {
        if(key !== 'reset'){
            f.value[key] = true;
        } else {
            f.value[key] = false;
        }
    });
}

watch(filters, (newValue) => {
    f.value = newValue
    if(newValue['reset'] === true) {
        resetFilters();
    }
})



</script>

<style scoped>

.author-row {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    border-top: solid 2px #f4e7fd;
    padding-top: 1ch;
}

.searchbar-row {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 1rem;
    border-top: solid 2px #f4e7fd;
    padding-top: 1ch;
}
.searchbar-item {
    text-align: start;
    display: flex;
    flex-direction: column;
    align-items: start;
    margin: .25rem 0;
    padding: .25rem 1rem;
    background-color: #fcf8ff;
    border-radius: 4px;
    transition: background 100ms ease-in;
    font-weight: 500;
}
.searchbar-item:hover {
    background-color: #f4e7fd;
    transition: background 100ms ease-in;
}

.searchbar-title {
    font-weight: 600;
    width: 120%;
    font-size: large;
}
</style>