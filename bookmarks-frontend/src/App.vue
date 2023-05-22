<template>
  <main class="w-screen h-100 bg-gray-100">
    <RouterView />
  </main>
</template>

<script>
  import SignUp from '@/views/signup.vue'
  
  export default {
    components: {
      SignUp
    }
  }
</script>

<style>
    html {
    --tw-bg-opacity: 1;
    background-color: rgb(243 244 246 / var(--tw-bg-opacity));
    }
</style>