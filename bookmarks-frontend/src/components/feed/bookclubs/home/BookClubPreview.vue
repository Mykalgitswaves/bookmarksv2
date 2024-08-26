<template>
    <div class="bookclub-preview">
        <img src="" alt="">
        <div class="metadata">
            <h3 class="title">
                {{ bookclub.title ? bookclub.title : 'loading'}}
            </h3>

            <p v-if="bookclub.currentlyReading">
                {{ currentlyReading }}
            </p>

            <a :href="navRoutes.toBookclub(bookclub.id)">Go to club</a>
        </div>
    </div>
</template>
<script setup>
import { navRoutes } from '../../../../services/urls';

const props = defineProps({
    bookclub: {
        type: Object,
        required: true,
    }
});

</script>
<style scoped>

.bookclub-preview {
    padding: 8px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--stone-300);
    display: flex;
    justify-content: space-around;
    max-width: 450px;
}

</style>