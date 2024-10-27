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

            <!-- Sticky toolbar containing buttons for creating and filtering posts -->
            <BookClubFeedActions @start-club-update-post-flow="showUpdateForm()" />

            <Overlay ref="updateOverlay">
                <template #overlay-header>

                </template>
                <template #overlay-main>
                    <CreateUpdateForm 
                        :book="club.currently_reading_book" 
                        @update-complete="(update) => postUpdateForBookClub(update)"
                    />
                </template>
            </Overlay>

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
import BookClubFeedActions from './BookClubFeedActions.vue';
import ClubPost from './posts/ClubPost.vue';
import Overlay from '@/components/feed/partials/overlay/Overlay.vue';
import CreateUpdateForm from '@/components/feed/createPosts/update/createUpdateForm.vue';
import { ref } from 'vue';
import { db } from '../../../../services/db';
import { urls } from '../../../../services/urls';

const props = defineProps({
    club: {
        type: Object,
        required: true,
    }
});

const data = ref({});
const loaded = ref(false);

const updateOverlay = ref(null);
function showUpdateForm() {
    const { dialogRef } = updateOverlay.value;
    dialogRef?.showModal();
};

/**
 * @load
 * @description – Reruns every time the club loads
 */
function loadClubFeed(){
    db.get(urls.bookclubs.getClubFeed(route.params.bookclub), null, false, (res) => {
        debugger;
        data.value = res;
    },
    (err) => {
        console.log(err);
    });
};



function postUpdateForBookClub(update) {
    db.post(urls.bookclubs.postUpdateForBookClub(route.params.bookclub), {}, false, 
        (res) => {
            console.log(res);
            // Refresh;
            loadClubFeed();
        },
        (err) => {
            console.warn(err);
        },
    );
};
</script>