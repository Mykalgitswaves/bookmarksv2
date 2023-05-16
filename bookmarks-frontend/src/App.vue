<template>
  <main class="w-screen h-screen bg-gray-100">
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