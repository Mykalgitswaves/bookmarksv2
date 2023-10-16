<template>
    <div>
        yo yo yo
    </div>
</template>
<script setup>
import { watch } from 'vue';
import { store } from './comparison';

watch(store.keys(), (newValue) => {
    console.log(newValue);
});

</script>