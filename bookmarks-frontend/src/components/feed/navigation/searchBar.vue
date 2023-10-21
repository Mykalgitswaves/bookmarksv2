<template>
    <div class="container searchbar ">
            <label for="searchbar"><span class="hidden">Search</span>
                <input
                    name="searchbar"
                    v-model="searchData"
                    @keyup="searchRequest(searchData)"
                    class="border-solid border-2
                    border-indigo-300 py-2 pl-2 rounded-md" 
                    type="text" placeholder=" What are you looking for?"
                />
            </label>
    </div>
    <div class="filter-grid">
        <button
            class="my-2 px-4 py-2 bg-indigo-900 text-white btn-transition rounded-md "
            :class="activeFilterMapping['reset'] ? 'active' : 'inactive'"
            type="button"
            name="resetFilters"
            @click="currentFilter = 'reset'"
        >
            Reset
        </button>

        <button 
            class="my-2 px-4 py-2 bg-indigo-900 text-white btn-transition  rounded-md "
            :class="activeFilterMapping['authors'] ? 'active' : 'inactive'"
            type="button"
            name="authorsFilter"
            @click="currentFilter = 'authors'"
        >
            Authors
        </button>

        <button 
            class="my-2 px-4 py-2 bg-indigo-900 text-white btn-transition  rounded-md "
            :class="activeFilterMapping['books'] ? 'active' : 'inactive'"
            type="button"
            name="booksFilters"
            @click="currentFilter = 'books'"
        >
            Books
        </button>

        <button 
            class="my-2 px-4 py-2 bg-indigo-900 text-white btn-transition  rounded-md "
            :class="activeFilterMapping['users'] ? 'active' : 'inactive'"
            type="button"
            name="usersFilters"
            @click="currentFilter = 'users'"
        >
            Users
        </button>
    </div>
</template>
<script setup>
import { ref, watch } from 'vue';
import { searchResultStore } from '@/stores/searchBar.js'; 

const responseBlob = ref(null);
const searchData = ref('');
const store = searchResultStore();
const emit = defineEmits();

const activeFilterMapping = ref({
    "authors": true,
    "users": true,
    "books": true,
    "genres": true,
    "reset": false,
});

// defaults to none.
const currentFilter = ref('');

// manually loop through each key in ref and turn to false.

watch(currentFilter, (newValue) => { 
    activeFilterMapping.value[newValue] = !activeFilterMapping.value[newValue];

    emit('toggle-filter', activeFilterMapping.value);
});


// Gets own specific search Request from here.
async function searchRequest(searchData) {
    if (searchData.length > 1) {
        try {
            return await fetch(`http://127.0.0.1:8000/api/search/${searchData}`) 
                .then((data) => data.json())
                .then(res => {
                    responseBlob.value = res.data;
                    store.saveAndLoadSearchResults(res.data);
                    emit('store-updated', store.data);
                });
        } catch(err) {
                return console.error(err);
        }
}}

</script>

<style scoped>

.hidden { display: none; visibility: hidden; }
.searchbar {
    color: #5A67D8;
    font-weight: 400;
}

.searchbar input {
    max-width: 300px;
    width: 100%;
}

.filter-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    justify-content: space-between;
    margin-top: 1ch;
    max-width: 400px;
}

.active {
    background-color: #1e1b4b;
    color: #e0e7ff;
}

.inactive {
    background-color: #c7d2fe;
    color: #1e1b4b;
}

.btn-transition {
    transition: all 250ms ease-in-out;
}
</style>