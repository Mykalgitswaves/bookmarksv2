<template>
    <h1>Search Results</h1>  

</template>

<script setup>
import { onMounted } from "vue"


const props = defineProps({
    data: {
        type: Array,
        default: null
    }
})



onMounted(() => {
    console.log(props.data)
})

</script>