<template>
    <div class="progress-bar-container">
        <span class="progress-bar" :style="{'width': (currentPage / totalPages) * 100 + '%'}"></span>
        <span class="progress-bar remainder" :style="{'width': (currentPage - totalPages / totalPages) * 100 + '%'}"></span>
    </div>
    <div class="update-previews">

    </div>
</template>
<script setup>
import { computed, ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { db } from '../../../services/db';
import { urls } from '../../../services/urls';

const props = defineProps({
    book: {
        type: Object,
        required: true,
    },
    currentPage: {
        type: Number,
    },
    totalPages: {
        type: Number,
    },
});

const updatePreviews = ref([]);
const loaded = ref(false);
const route = useRoute();

function successFunction(data) {
    updatePreviews.value = data.res.updates;
    loaded.value = true;
}

onMounted(async () => {
    // #TODO: Fix this so that it calls updates for books in a shelf so we can render previews for them inside update bookshelves.
    await db.get(urls.rtc.updatesByBookInCurrentlyReading(route.params.user, props.book.id), {}, null, successFunction, null);
});
</script>
<style scoped>
.progress-bar-container {
    display: flex;
    margin-top: 12px;
    margin-bottom: 4px;
    border-radius: 4px;
    overflow: clip
}

.progress-bar {
 height: 2px;
 background-color: var(--stone-200);
 display: inline-block;

 &.remainder {
    width: auto;
    background-color: var(--stone-100);
 }
}
</style>