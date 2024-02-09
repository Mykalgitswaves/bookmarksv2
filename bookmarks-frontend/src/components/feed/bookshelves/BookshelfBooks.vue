<template>
    <ul class="bookshelf-books">
        <BookshelfBook 
            v-for="book in books"
            :key="book?.order"
            :book="book"
            @up="(order) => bookUpwards(order)"
            @down="(order) => bookDownwards(order)"
        />
    </ul>
</template>
<script setup>
import BookshelfBook from './BookshelfBook.vue';

const props = defineProps({
    books: {
        type: Array,
    }
})

function bookUpwards(order) {
    console.log(order);
}

function bookDownwards(order){
    console.log(order);
}
</script>
<style scoped lang="scss">
    .bookshelf-books {
        display: grid;
        padding-top: var(--padding-sm);
        row-gap: 8px;
    }
</style>