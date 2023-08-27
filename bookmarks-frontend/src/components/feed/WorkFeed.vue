<template>
  <div class="relative">
      <SearchResults/>

      <h2 class="pt-4 text-2xl font-medium text-slate-600 mb-5">Recommended Works</h2>
      <div class="card-grids">
      


      <WorkCard 
        v-for="(work, index) in books" 
        :key="index" 
        :work="work"
        :user="user"
      />

      </div>
  </div>
</template>
<script setup>
      import { ref, toRaw, computed, defineAsyncComponent, onBeforeMount, watch } from 'vue';
      import { useRoute } from "vue-router";
      import { db } from '@/services/db.js';
      import { urls } from '@/services/urls.js';
      import { searchResultStore } from '@/stores/searchBar.js'
      import LoadingWorkCard from '../loading/WorkCard.vue';
      import ErrorWorkCard from '../error/WorkCard.vue';
      import SearchResults from '@/components/feed/navigation/SearchResults.vue';

      const route = useRoute();
    // let componentState = headerMapping[0]
      const user = route.params.user;

      const loading = [{
        title: 'Loading',
        genres: ['good', 'comes', 'to', 'those', 'who', 'wait']
      }];

      const bookData = ref([]);

      async function getWorks() {
        bookData.value = await db.get(urls.booksByN, {'limit': 25})
      }

      onBeforeMount(() => {
        return getWorks()
      });

      const store = searchResultStore();

      watch(bookData.value, (oldValue, newValue) => {
        if(oldValue, newValue) {
          store.saveAndLoadSearchResults(newValue);
        }
      })

      const books = computed(() => bookData.value.length ? toRaw(bookData.value) : loading)
      // const loaded = computed(() => bookData.value.length ? true : false)

      const WorkCard = defineAsyncComponent({
        loader: () => import('./WorkCard.vue'),
        loadingComponent: LoadingWorkCard,
        errorComponent: ErrorWorkCard,
        delay: 200,
        timeout: 3000
      })
</script>

<style scoped>
  .card-grids {
    display: grid;
    grid-template-columns: 1;
    row-gap: 1.5rem;
  }
</style>