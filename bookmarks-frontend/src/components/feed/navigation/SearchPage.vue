<template>
  <div class="search-page-wrapper bg-slate-50 rounded-lg shadow-md">
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
        height: 100%;
        padding: 2rem 3rem;
    }

</style>