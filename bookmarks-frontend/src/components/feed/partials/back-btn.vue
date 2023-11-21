<template>
    <button
    type="button"
    class="flex ml-5 my-2 text-indigo-600 items-center md:ml-10 back-hover"
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
<style scoped>
.back-hover {
  transition: 250ms ease;
  padding: 4px 12px;
  border-radius: 4px;
  border: 1px solid #fff;
  width: 100px;
  justify-content: center;
}

.back-hover:hover {
  background-color: #e0e7ff;
  border: 1px solid #e0e7ff;
}

.back-btn:active {
  border-color: #768bf7
}
</style>