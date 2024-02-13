<template>
    <ul class="bookshelf-books" ref="books" v-if="bookElements.length">
        <sort-item
            v-for="item in bookElements"
            :key="item.order"
            :order="item.order" 
            :name="item.name"
            :bookTitle="item.bookTitle"
            :author="item.author"
            :imgUrl="item.imgUrl"
        ></sort-item>
    </ul>
</template>
<script setup>
import { items } from './bookshelvesRtc';
import { ref, onMounted } from 'vue';

const books = ref(null);
const bookElements = ref([]);

onMounted(() => {
    items.forEach((item) => {
        let props = {
            order: item.order, 
            name: item.id,
            bookTitle: item.bookTitle,
            author: item.author,
            imgUrl: item.imgUrl
        };

        // let book = new SortItem(item.order, item.id, item.bookTitle, item.author, item.imgUrl);
        bookElements.value.push(props);

        // constructor(order, name, bookTitle, author, imgUrl) {
        // super();
        // this.order = order;
        // this.name = name;
        // this.bookTitle = bookTitle;
        // this.author = author;
        // this.imgUrl = imgUrl;
    });
});
</script>
<style scoped lang="scss">
    .bookshelf-books {
        display: grid;
        padding-top: var(--padding-sm);
        row-gap: 8px;
    }
</style>