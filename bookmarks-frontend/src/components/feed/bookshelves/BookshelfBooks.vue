<template>
    <ul class="bookshelf-books" v-if="bookElements.length">
        <sort-item
            v-for="item in bookElements"
            :key="item.id"
            :order="item.order" 
            :_id="item.id"
            :bookTitle="item.bookTitle"
            :author="item.author"
            :imgUrl="item.imgUrl"
            @reordered="($event) => handleReorder($event)"
        ></sort-item>
    </ul>
</template>
<script setup>
import { items } from './bookshelvesRtc';
import { ref } from 'vue';

const bookElements = ref([]);

items.forEach((item) => {
    let props = {
        order: item.order, 
        id: item.id,
        bookTitle: item.bookTitle,
        author: item.author,
        imgUrl: item.imgUrl
    };

    bookElements.value.push(props);
});

function handleReorder(data){
    const d = data;
    console.log(d)
}
</script>
<style scoped lang="scss">
    .bookshelf-books {
        display: grid;
        padding-top: var(--padding-sm);
        row-gap: 8px;
    }
</style>