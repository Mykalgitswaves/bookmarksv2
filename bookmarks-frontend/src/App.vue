<template>
  <main class="w-100 h-100 bg-gray-100">
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