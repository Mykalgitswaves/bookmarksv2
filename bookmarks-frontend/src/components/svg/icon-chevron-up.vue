<template>
    <svg :class="attrs?.class" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M18.78 15.78a.749.749 0 0 1-1.06 0L12 10.061 6.28 15.78a.749.749 0 1 1-1.06-1.06l6.25-6.25a.749.749 0 0 1 1.06 0l6.25 6.25a.749.749 0 0 1 0 1.06Z"></path></svg>
</template>
<script setup>
import {useAttrs} from 'vue';
const attrs = useAttrs();
</script>