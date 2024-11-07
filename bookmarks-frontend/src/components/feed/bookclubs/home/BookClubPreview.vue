<template>
    <div class="bookclub-preview">

        <!-- Hold off on this until I get an href working... -->
        <img v-if="bookclub?.currently_reading_book?.small_img_url"
            class="currently-reading-img" 
            :src="bookclub.currently_reading_book.small_img_url" 
            alt="" 
        />

        <div class="metadata" v-if="bookclub">
            <div>
                <h3 class="title">
                    {{ bookclub.book_club_name}}
                </h3>

                <p v-if="bookclub.currently_reading_book" class="currently-reading">
                    Currently Reading: <i>{{ bookclub.currently_reading_book.title }}</i>
                </p>

                <p v-else class="currently-reading">Not currently reading anything</p>
            </div>

            <a class="link" :href="navRoutes.toBookClubFeed(user, bookclub.book_club_id)">Go to club</a>
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
    flex-direction: row-reverse;
    align-items: center;
    column-gap: 20px;
    width: fit-content;
    /* max-width: 1fr; */

    & .title {
        font-size: var(--font-2xl);
        font-family: var(--fancy-script);
        color: var(--stone-700);
    }

    & .currently-reading {
        color: var(--stone-500);
        font-size: var(--font-sm);
    }

    & .currently-reading-img {
        height: 80%;
        border-radius: var(--radius-sm);
    }

    & .link {
        padding-top: 30px;
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