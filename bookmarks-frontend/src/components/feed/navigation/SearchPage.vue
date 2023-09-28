<template>
  <div class="search-page-wrapper border-solid border-indigo-100 border-[1px]">
    <SearchBar 
        @store-updated="storeHandler" 
        @toggle-filter="filterHandler"
    />

      <p class="pt-4 text-2xl font-medium text-slate-600 mb-5">Search Results</p>
      
      <SearchResult :new-data="newData" :filters="filters"/>
  </div>  
</template>
<script setup>

import { ref, } from 'vue';
import SearchResult from './SearchResults.vue';
import SearchBar from './searchBar.vue';



const newData = ref(null);

// create default filters
const filters = ref({});

function storeHandler(newBook) {
    newData.value = newBook
}

function filterHandler(activeFilter) {
    console.log(activeFilter)
    filters.value = activeFilter;
}

</script>

<style scoped>
    :root {
        --padding: 
    }
    .search-page-wrapper {
        height: 100%;
        padding: 2rem 3rem;
        background: var(--background-container-gradient);
        border-radius: 1rem;
    }

    @media screen and (min-width: 768px) {
        .search-page-wrapper {
            padding: 1.5rem;
        }
        
    }
</style>