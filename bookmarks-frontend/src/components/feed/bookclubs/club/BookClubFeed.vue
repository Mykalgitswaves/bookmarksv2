<template>
        <div class="bookclub-header flex justify-between items-start">
            <div>
                <h1 class="text-3xl fancy text-stone-700">
                    {{ club?.book_club_name }}
                </h1>
                
                <p class="text-stone-500 mt-5">
                    {{ club?.description || 'Add a description for your book club' }}    
                </p>
            </div>

            <button type="button" class="pt-5 text-stone-500">
                <span class="visually-hidden">Settings</span>
                
                <IconSettings />
            </button>
        </div>

        <section class="club-main-padding" v-if="loaded">
            <CurrentlyReadingBook 
                :book="currentlyReadingBook" 
                @currently-reading-settings=""
            />

            <CurrentPacesForClubBook :total-chapters="currentlyReadingBook?.chapters"/>

            <!-- Sticky toolbar containing buttons for creating and filtering posts -->
            <BookClubFeedActions 
                v-if="currentlyReadingBook"
                @start-club-update-post-flow="showUpdateForm()"
                @finished-reading="showFinishedReadingForm()"
            />

            <Overlay :ref="(el) => overlays.updateOverlay = el">
                <template #overlay-header>

                </template>
                <template #overlay-main>
                    <CreateUpdateForm 
                        style="width: 768px; margin-left: auto; margin-right: auto;"
                        :book="currentlyReadingBook" 
                        @post-update="(update) => postUpdateForBookClub(update)"
                    />
                </template>
            </Overlay>

            <Overlay :ref="(el) => overlays.finishedReadingOverlay = el">
                <template #overlay-header>

                </template>
                <template #overlay-main>
                        <CreateReviewPost 
                            :book="currentlyReadingBook"
                            unique="bookclub"
                            @is-postable-data="setPostData" 
                            @post-data="postToEndpoint()"
                        />
                </template>
            </Overlay>

            <!-- index for now until we can grab the id from the updates -->
            <ClubPost
                v-for="(post, index) in data.posts" 
                :key="index" 
                :post="post"
            />
        </section>

        <LoadingCard v-else />

        <div class="mobile-menu-spacer sm:hidden"></div>
</template>
<script setup>
import CurrentlyReadingBook from './CurrentlyReadingBook.vue';
import BookClubFeedActions from './BookClubFeedActions.vue';
import ClubPost from './posts/ClubPost.vue';
import Overlay from '@/components/feed/partials/overlay/Overlay.vue';
import CreateUpdateForm from '@/components/feed/createPosts/update/createUpdateForm.vue';
import CreateReviewPost  from '@/components/feed/createPosts/createReviewPost.vue';
import CurrentPacesForClubBook from './CurrentPacesForClubBook.vue';
import { ref } from 'vue';
import { db } from '../../../../services/db';
import { urls } from '../../../../services/urls';
import { formatUpdateForBookClub } from '../bookClubService';
import { useRoute } from 'vue-router';
import LoadingCard from '../../../shared/LoadingCard.vue';


const props = defineProps({
    club: {
        type: Object,
        required: true,
    }
});

const data = ref({
    posts: [],
});
const loaded = ref(false);

const overlays = ref({
    updateOverlay: null,
    finishedReadingOverlay: null,
});

const route = useRoute();

let currentlyReadingBook = {};

function showUpdateForm() {
    const { dialogRef } = overlays.value.updateOverlay;
    dialogRef?.showModal();
};

function showFinishedReadingForm() {
    const { dialogRef } = overlays.value.finishedReadingOverlay;
    dialogRef?.showModal(); 
}

/**
 * @load
 * @description – Reruns every time the club loads
 */

const clubFeedPromise = db.get(urls.bookclubs.getClubFeed(route.params.bookclub), null, false, (res) => {
    data.value.posts = res.posts;
},
(err) => {
    console.log(err);
});

const currentlyReadingPromise = db.get(urls.bookclubs.getCurrentlyReadingForClub(route.params.bookclub), null, false, (res) => {
    currentlyReadingBook = res.currently_reading_book;
});

Promise.all([clubFeedPromise, currentlyReadingPromise]).then(() => {
    loaded.value = true;
});

// So users can scroll up and refresh feed. 
function refreshFeed() {
    loaded.value = false;
    Promise.resolve(clubFeedPromise).then(() => {
        loaded.value = true;
    });
}

/**
 * @post
 */

function postUpdateForBookClub(update) {
    update = formatUpdateForBookClub(update, route.params.user)

    db.post(urls.bookclubs.createClubUpdate(route.params.bookclub), update, false, 
        (res) => {
            console.log(res);
            // Refresh;
            refreshFeed();
            const { dialogRef } = overlays.value.updateOverlay;
            dialogRef?.close();
        },
        (err) => {
            console.warn(err);
        },
    );
};
</script>