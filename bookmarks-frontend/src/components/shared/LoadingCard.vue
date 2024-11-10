<template>
    <div class="loading-card gradient" 
        :style="{ 'height': attributes.height || '100px'}"
    >
        <div class="gradient element1"></div>
        
        <!-- <div class="gradient element2"></div>
        
        <div class="gradient element3"></div>
        
        
        <div class="gradient element4"></div>
        
        <div class="gradient element5"></div> -->
    </div>
</template>
<script setup>
import { useAttrs } from 'vue';
const attributes = useAttrs();
</script>
<style scoped>
  /* Loading card */
  .loading-card {
    width: 70%;
    max-height: 550px;
    margin: 16px auto;
    background-color: var(--surface-primary);
    border-radius: var(--radius-md);
    -webkit-box-shadow: var(--shadow-lg);
    -moz-box-shadow: var(--shadow-lg);
    box-shadow: var(--shadow-lg);
  }

  .element1 {
      top: 14%;
      left: 50%;
      transform: translate(-50%, -50%);
      height: 15%;
      width: 50%;
      border-radius: var(--radius-sm)
  }

  .element2 {
      top: 22%;
      left: 80px;
      height: 68px;
      width: 80%;
  }

  .element3 {
      top: 30%;
      left: 16px;
      height: 14px;
      width: 80%;
  }

  .element4 {
      top: 36%;
      left: 16px;
      height: 14px;
      width: 80%;
  }
</style>