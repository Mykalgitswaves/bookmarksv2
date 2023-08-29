<template>
    <div class="container searchbar ">
            <label for="searchbar"><span class="hidden">Search</span>
                <input 
                    name="searchbar"
                    v-model="searchData"
                    @keydown="searchRequest(searchData)"
                    class="border-solid border-2
                    border-indigo-300 py-2 pl-2 rounded-md" 
                    type="text" placeholder=" What are you looking for?"
                />
            </label>
    </div>
    <div class="filter-grid">
        <button
            :class="'my-2 px-4 py-2 bg-indigo-900 text-indigo-100 rounded-lg ' + hoverStyles"
            type="button"
            name="resetFilters"
            @click="resetFilters"
        >
            All
        </button>

        <button 
            :class="'my-2 px-4 py-2 bg-indigo-900 text-indigo-100 rounded-lg ' + hoverStyles"
            type="button"
            name="authorsFilter"
            @click="toggleAuthorFilter"
        >
            Authors
        </button>

        <button 
            :class="'my-2 px-4 py-2 bg-indigo-900 text-indigo-100 rounded-lg ' + hoverStyles"
            type="button"
            name="booksFilters"
            @click="toggleBooksFilter"
        >
            Books
        </button>

        <button 
            :class="'my-2 px-4 py-2 bg-indigo-900 text-indigo-100 rounded-lg ' + hoverStyles"
            type="button"
            name="usersFilters"
            @click="toggleUsersFilter"
        >
            Users
        </button>
    </div>
</template>
<script setup>
    import { ref } from 'vue';
    import { searchResultStore } from '@/stores/searchBar.js'; 
    const hoverStyles = 'hover:bg-indigo-100'

    const responseBlob = ref(null);
    const searchData = ref('');
    const store = searchResultStore();

    async function searchRequest(searchData) {
        if (searchData.length > 1) {
            try {
                return await fetch(`http://127.0.0.1:8000/api/search/${searchData}`) 
                    .then((data) => data.json())
                    .then(res => {
                        responseBlob.value = res.data;
                        store.saveAndLoadSearchResults(res.data);
                        console.log(store.data);
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
    width: 280px;
}

.filter-grid {
    display: flex;
    gap: 10px;
}
.filter-grid button:hover { color: #26318b;} 

</style>