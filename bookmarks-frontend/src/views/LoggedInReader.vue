<template>
  <TopNav/>
  <div class="sidebar">
    <div class="main-layout">  
      <RouterView></RouterView>
    </div>
    <FooterNav/>
  </div>
</template>
<script setup>
import TopNav from '@/components/feed/topnav.vue';
import FooterNav from '@/components/feed/footernav.vue'

import { onMounted } from "vue";
import { useRoute } from 'vue-router';
import { db } from '../services/db'
import { urls } from '../services/urls'

const route = useRoute();

onMounted(() => {
  db.authenticate(urls.authUrl, route.params.user);
});
</script>
<style scoped>
  .main-layout {
    min-height: 100%;
    width: 100%;
    padding: 1.25rem;
    gap: 2ch;
    justify-content: center;
  }

  @media only screen and (min-width: 768px) {
    .main-layout {
      justify-content: start;
      padding-left: 12vw;
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

