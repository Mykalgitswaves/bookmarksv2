<template>
    <div class="bookclub-preview">

        <!-- Hold off on this until I get an href working... -->
        <!-- <img src="" alt="" /> -->

        <div class="placeholder"></div>

        <div class="metadata">
            <h3 class="title">
                {{ bookclub.book_club_name}}
            </h3>

            <p v-if="bookclub.currently_reading_book" class="currently-reading">
                {{ bookclub.currently_reading_book }}
            </p>
            <p v-else class="currently-reading">Not currently reading</p>

            <a class="link" :href="navRoutes.toBookClub(user, bookclub.book_club_id)">Go to club</a>
        </div>
    </div>
</template>
<script setup>
import { navRoutes } from '../../../../services/urls';

const props = defineProps({
    bookclub: {
        type: Object,
        required: true,
    },
    user: {
        type: String,
        required: false,
    }
});

</script>
<style scoped>

.bookclub-preview {
    padding: 14px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--stone-300);
    display: flex;
    justify-content: start;
    align-items: center;
    column-gap: 14px;
    width: fit-content;
    /* max-width: 1fr; */

    & .title {
        font-size: var(--font-2xl);
        font-family: var(--fancy-script);
        color: var(--stone-700);
    }

    & .currently-reading {
        color: var(--stone-500);
        margin-bottom: 12px;
        font-size: var(--font-sm);
    }

    & .link {
        color: var(--blue-400);
        font-size: var(--font-sm);
        text-decoration: underline;
    }
}

.placeholder {
    background-color: var(--stone-200);
    width: 70px;
    height: 100px;
}

</style>