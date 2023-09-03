<template>
  <TopNav :profilePicture="profilePicture"/>
  <div class="sidebar">
    <div class="bg-gray-200 main-layout">  
      <RouterView></RouterView>
    </div>
    <FooterNav/>
</div>
</template>

<script setup>

  import TopNav from '@/components/feed/topnav.vue';

  import FooterNav from '@/components/feed/footernav.vue'
  import profilePicture from '@/assets/profileimage.jpg'
  import { onMounted } from "vue";
  import { useRoute } from 'vue-router';
  import { db } from '../services/db'
  import { urls } from '../services/urls'

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

      const route = useRoute();
      onMounted(() => {
        // Passing strings of url and uuid to authenticate function.
        return db.authenticate(urls.authUrl, route.params.user);
      });
</script>
<style scoped>
  .main-layout {
    min-height: 80vh;
    width: 100%;
    padding: 1.25rem;
    gap: 2ch;
    justify-content: center;
  }

  @media only screen and (min-width: 768px) {
    .main-layout {
      justify-content: start;
      padding-left: 3rem;
    }
    .sidebar {
      display: flex;
      flex-direction: row-reverse;
      justify-content: space-between;
    }
  }

  @media only screen and (min-width: 960px) {
    .main-layout {
      margin-left: 0rem;
    }
  }
</style>

