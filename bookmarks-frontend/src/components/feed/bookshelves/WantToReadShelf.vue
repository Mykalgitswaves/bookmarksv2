<template>
    <div class="bookshelf-heading">
        <div>
            <h1 class="bookshelf-title">{{ bookshelfData?.title || 'Untitled'}}</h1>

            <p class="bookshelf-description">{{ bookshelfData?.description || 'Add a description'}}</p>
        </div>

        <button
            v-if="isAdmin"
            type="button"
            class="btn edit-btn"
            @click="goToBookshelfSettingsPage(router, route.params.user, route.params.bookshelf)"
        >
            <IconEdit/>
        </button>
    </div>
</template>
<script setup>
import {onMounted, ref} from 'vue';
import { useRoute } from 'vue-router';
import { getWantToReadshelfPromise } from './wantToRead.js';

const route = useRoute();
const { bookshelf } = route.params;
const bookshelfData = ref(null);
const loaded = ref(false);

onMounted(async() => {
    const wantToReadShelfPromise = await getWantToReadshelfPromise(bookshelf);
    Promise.all([wantToReadShelfPromise]).then(([wantToReadShelf]) => {
        bookshelfData.value = wantToReadShelf.bookshelf;
        loaded.value = true;
    });
});
</script>