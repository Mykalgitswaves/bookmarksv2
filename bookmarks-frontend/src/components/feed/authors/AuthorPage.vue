<template>
<div class="container">
    



</div>
</template>
<script setup>
import { db } from '@/services/db.js'
import { urls } from '@/services/urls.js';
import { useRoute } from 'vue-router';
import { ref } from 'vue';

const route = useRoute();

const author = ref(null)

async function getData() {
    author.value = await db.get(urls.author, {'book': route.params.author}, true);
    console.log(author.value)
}
getData()


</script>