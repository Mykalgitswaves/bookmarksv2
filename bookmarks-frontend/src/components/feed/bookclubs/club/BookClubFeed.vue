<template>
        <div class="bookclub-header flex justify-between items-start">
            <div>
                <h1 class="text-3xl fancy text-stone-700">
                    {{ club.book_club_name }}
                </h1>
                
                <p class="text-stone-500 mt-5">
                    {{ club.description || 'Add a description for your book club' }}    
                </p>
            </div>

            <button type="button" class="pt-5 text-stone-500">
                <span class="visually-hidden">Settings</span>
                
                <IconSettings />
            </button>
        </div>

        <div class="club-main-padding">
            <CurrentlyReadingBook 
                :book="club.currently_reading_book" 
                @currently-reading-settings=""
            />

            <div v-if="loaded">
                <!-- index for now until we can grab the id from the updates -->
                <ClubPost
                    v-for="(post, index) in posts" 
                    :key="index" 
                    :post="post"
                />
            </div>
        </div>
</template>
<script setup>
import CurrentlyReadingBook from './CurrentlyReadingBook.vue';
import ClubPost from './posts/ClubPost.vue';
import { ref } from 'vue';
import { db } from '../../../../services/db';
import { urls } from '../../../../services/urls';

const props = defineProps({
    club: {
        type: Object,
        required: true,
    }
});

let bookClubPosts = [];
const loaded = ref(false);

/**
 * @load_data
 * @description – Reruns every time the club loads
 */
// db.get(urls.bookclubs.getClubFeed(props.club.book_club_id), 
//     null,
//     false,
//     (res) => {
//         bookClubPosts = res.updates
//         loaded.value = true;
//     }, (err) => {
//         errors = err;
//         loaded.value = true;
//     }
// );
</script>