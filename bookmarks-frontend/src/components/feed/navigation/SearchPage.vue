<template>
  <div class="container search-page-wrapper bg-slate-300 rounded-lg shadow-md">
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
    .search-page-wrapper {
        width: 100%;
        height: 100%;
        min-width: 60vw;
        min-height: 60vh;
        padding: 2rem 1rem;
    }

</style>