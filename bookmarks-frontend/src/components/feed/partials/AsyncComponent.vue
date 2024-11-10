<template>
    <slot name="resolved" v-if="loaded">

    </slot>
    <slot name="loading" v-else>

    </slot>
</template>
<script setup>
// --------------------------------------------------------
// Async component for a generic loading state so you don't 
// have to keep on adding loaded logic all over the place;
// --------------------------------------------------------
import { ref } from 'vue';

const props = defineProps({
    promises: {
        type: Array[Promise],
        required: true,
    },
});

const loaded = ref(false);

Promise.all(props.promises).then(() => {
    loaded.value = true;
});
</script>