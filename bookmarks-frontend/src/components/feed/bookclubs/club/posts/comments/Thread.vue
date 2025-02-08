<template>
    yo world
</template>
<script setup lang="ts">
interface Thread {
    
}

const props = defineProps({
    thread: {
        type: Object,
        required: false, // false for now.
    }
});
</script>