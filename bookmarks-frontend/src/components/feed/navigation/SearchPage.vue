<template>
  <div class="search-page-wrapper">
    <SearchBar 
        @store-updated="storeHandler" 
        @toggle-filter="filterHandler"
    />
      
    <SearchResult :new-data="newData" :filters="filters"/>
  </div>
  <div class="mobile-menu-spacer sm:hidden"></div>
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
        height: fit-content;
        min-height: 166px;
        padding: 2rem var(--margin-md);
        background-color: var(--surface-primary);
        border-radius: 1rem;
        border: 1px var(--indigo-100) solid;
        max-width: var(--section-max-width);
        margin-right: auto;
        margin-left: auto;
    }

    @media screen and (min-width: 768px) {
        .search-page-wrapper {
            padding: 1.5rem;
        }
        
    }
</style>