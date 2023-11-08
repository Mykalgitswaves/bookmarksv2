<template>
    <button
    type="button"
    class="flex ml-5 my-2 text-indigo-600 items-center md:ml-10"
    @click="router.back()"
  >
    <IconBack/>
    <span class="ml-2">Back</span>
  </button>
</template>
<script setup>
import { useRouter } from 'vue-router';
import IconBack from '../../svg/icon-back.vue';

const router = useRouter();

</script>