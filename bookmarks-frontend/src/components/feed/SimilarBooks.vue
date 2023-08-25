<template>
    <h1>Similar Books</h1>
</template>
<script setup>
    import { ref } from 'vue';
    import { useRoute } from 'vue-router';
    
    const data = ref(null)

    async function getSimilarBooks(){
        try {
            const route = useRoute()
            const book_id = route.params.work
            console.log(route.params)
            const response = await fetch(`http://127.0.0.1:8000/api/books/${book_id}/similar`);
            const res = response.json();
            data.value = res
            console.log(res, 'front end boyt shit')
        } catch(error) {
            console.log(error)
        }
    }    

    getSimilarBooks()

</script>