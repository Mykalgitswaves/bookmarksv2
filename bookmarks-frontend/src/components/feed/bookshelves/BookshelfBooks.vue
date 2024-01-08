<template>
    <ul class="bookshelf-books">
        <div 
            v-for="(book, index) in books"
            :key="index"
            class=""
        >
            
    </div>
    </ul>
</template>
<script setup>
const props = defineProps({
    books: {
        type: Array,
    }
})
</script>
<style scoped>
    .bookshelf-books {
        
    }

    .books {

    }
</style>