<template>
  <div class="relative">
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
      import { ref, toRaw, computed, defineAsyncComponent, onBeforeMount, watch, onMounted } from 'vue';
      import { useRoute } from "vue-router";
      import { db } from '@/services/db.js';
      import { urls } from '@/services/urls.js';
      import { searchResultStore } from '@/stores/searchBar.js'
      import LoadingWorkCard from '../loading/WorkCard.vue';
      import ErrorWorkCard from '../error/WorkCard.vue';

      const route = useRoute();
    // let componentState = headerMapping[0]
      const user = route.params.user;

      const loading = [{
        title: 'Loading ',
        genres: ['good', 'comes', 'to', 'those', 'who', 'wait']
      }];

      const bookData = ref(null);

      onMounted(() => {
        bookData.value = db.get(urls.booksByN, {'limit': 25}, true)
      })
      
      // const store = searchResultStore();

      const books = computed(() => (bookData.value))
      // const loaded = computed(() => bookData.value.length ? true : false)
      watch(bookData, (oldValue, newValue) => {
        console.log(newValue, oldValue)
      })

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