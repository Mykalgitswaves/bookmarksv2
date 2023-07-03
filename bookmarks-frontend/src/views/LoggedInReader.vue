<template>
  <TopNav :profilePicture="profilePicture"/>
  <div class="bg-gray-200 main-layout">  
    <RouterView></RouterView>
  </div>
  <FooterNav/>
</template>

<script setup>

  import TopNav from '@/components/feed/topnav.vue';

  import FooterNav from '@/components/feed/footernav.vue'
  import profilePicture from '@/assets/profileimage.jpg'
  import { onMounted } from "vue";

// const headerMapping = {
//   0: BookReviews,
//   1: RecommendedBooks
// }

    // dynamicComponentState(index) {
    //   this.componentState = headerMapping[index]
    // }

  // computed: {
    // currentState() {
    //   return this.componentState
    // }

</script>
<style scoped>

.main-layout {
  min-height: 80vh;
  padding: 1.25rem;
  display: grid;
  grid-template-columns: 1;
  grid-auto-rows: minmax(min-content, max-content);
  gap: 2ch;
}



</style>

