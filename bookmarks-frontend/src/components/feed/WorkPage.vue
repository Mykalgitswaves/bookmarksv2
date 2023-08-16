<template>
   CashMoneyLoaded {{ data }}
   <SimilarBooks/>
</template>

<script setup>
import SimilarBooks from '@/components/feed/SimilarBooks.vue';
import {ref } from 'vue';
import { useRoute } from 'vue-router'

const data = ref(null);

async function getWorkPage(){
    const route = useRoute()
    const book_id = route.params.work
    console.log(route.params)
    await fetch(`http://127.0.0.1:8000/api/books/${book_id}`)
    .then((data) => data.json())
    .then((res) => {
        data.value = res.data
        console.log(res.data)
    })
}

getWorkPage()
</script>