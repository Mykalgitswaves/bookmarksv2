<template>
  <div class="search-page-wrapper">
      <SearchBar/> 

      <p class="pt-4 text-2xl font-medium text-slate-600 mb-5">Search Results</p>
      
      <SearchResult/>
  </div>  
</template>
<script setup>
import SearchResult from './SearchResults.vue';
import SearchBar from './searchBar.vue';


</script>

<style scoped>
    :root {
        --padding: 2rem 3rem;
    }
    .search-page-wrapper {
        height: 100%;
        padding: var(--padding);
        background: var(--background-container-gradient);
        border-radius: 1rem;
    }
    @media screen and (min-width: 768px) {
        :root {
            --padding: 1.5rem;
        }
    }
</style>