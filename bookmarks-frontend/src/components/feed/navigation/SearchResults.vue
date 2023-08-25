<template>
    <div class="container">
        <h1>Search Results</h1>  
        <ul>
            <li>
                
            </li>
        </ul>
    </div>
</template>

<script setup>
import { onMounted, watch, toRaw } from "vue"
import { useStore } from '@/stores/searchBar.js';

const searchResultStore = useStore()
const rawData = searchResultStore.data
const data = toRaw(rawData);

onMounted(() => {
    console.log(data)
})

</script>