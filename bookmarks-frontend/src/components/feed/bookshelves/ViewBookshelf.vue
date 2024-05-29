<template>
    <WantToReadShelf v-if="isWantToRead"/>

    <EditBookshelf v-else/>
</template>
<script setup>
import EditBookshelf from './EditBookshelf.vue';
import WantToReadShelf from './WantToReadShelf.vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const isWantToRead = !!route.params.bookshelf.includes('want_to_read');
</script>