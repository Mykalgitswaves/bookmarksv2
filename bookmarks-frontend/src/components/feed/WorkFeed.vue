<template>
    <h2 class="pt-4 text-2xl font-medium text-slate-600">Recommended Works</h2>
    <KeepAlive>
      <WorkCard 
        v-for="(c, index) in cards" 
        :key="index" 
        :placeholderBookImg="placeholderBookImg"
        :card="c"
        :user="user"
      />
    </KeepAlive>
</template>
<script setup>
      import placeholderBookImg from '@/assets/infiniteJest.png'
      import WorkCard from '@/components/feed/WorkCard.vue';
      import { useRoute } from "vue-router"
      const route = useRoute();
    // let componentState = headerMapping[0]
      let cards = [1, 2, 3, 4, 5]
  
      const user = route.params.user
</script>