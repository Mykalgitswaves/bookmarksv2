<template>
  <div class="search-page-wrapper">
    <SearchBar 
        @store-updated="storeHandler" 
        @toggle-filter="filterHandler"
    />
      
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
        border: 1px var(--indigo-100) solid;
        max-width: var(--section-max-width);
    }

    @media screen and (min-width: 768px) {
        .search-page-wrapper {
            padding: 1.5rem;
        }
        
    }
</style>