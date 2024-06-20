<template>
    <WantToReadShelf v-if="isWantToRead" />

    <CurrentlyReadingShelf v-if="isCurrentlyReading" />

    <EditBookshelf v-else />

</template>
<script setup>
import EditBookshelf from './EditBookshelf.vue';
import WantToReadShelf from './WantToReadShelf.vue';
import CurrentlyReadingShelf from './CurrentlyReadingShelf.vue';
import { useRoute } from 'vue-router';

const props = defineProps({
    bookshelf: {
        type: Object,
    },
});

const route = useRoute();
const isWantToRead = !!route.params.bookshelf.includes('want_to_read');
const isCurrentlyReading = !!route.params.bookshelf.includes('currently_reading');
</script>