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

        <section v-if="loaded" 
            class="club-main-padding"
            :class="{
                'is-user-finished-with-current-book': club.currently_reading_book.is_user_finished_reading
            }"
        >
            <CurrentlyReadingBook 
                :is-finished-reading="currentlyReadingBook.is_user_finished_reading"
                :book="currentlyReadingBook" 
                @currently-reading-settings="router.push(
                    navRoutes.bookClubSettingsCurrentlyReading(
                        route.params.user, 
                        route.params.bookclub
                    )
                )"
            />

            <CurrentPacesForClubBook :total-chapters="currentlyReadingBook?.chapters"/>

            <!-- Sticky toolbar containing buttons for creating and filtering posts -->
            <BookClubFeedActions 
                v-if="currentlyReadingBook"
                @start-club-update-post-flow="showUpdateForm()"
                @finished-reading="showFinishedReadingForm()"
            />

            <Overlay :ref="(el) => overlays.updateOverlay = el?.dialogRef">
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

            <Overlay :ref="(el) => overlays.finishedReadingOverlay = el?.dialogRef">
                <template #overlay-header>

                </template>
                <template #overlay-main>
                        <CreateReviewPost 
                            :book="currentlyReadingBook"
                            unique="bookclub"
                            @is-postable-data="(post) => reviewPost = post" 
                            @post-data="postReviewAndFinishReadingCurrentBook(reviewPost)"
                            @user-skipped-review="postReviewAndFinishReadingCurrentBook(null)"
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
import { ref, watch } from 'vue';
import { db } from '../../../../services/db';
import { navRoutes, urls } from '../../../../services/urls';
import { formatUpdateForBookClub } from '../bookClubService';
import { useRoute, useRouter } from 'vue-router';
import LoadingCard from '../../../shared/LoadingCard.vue';
import { createConfetti } from '../../../../services/helpers';
import { currentUser } from '../../../../stores/currentUser.ts';

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
    wrappedOverlay: null,
});

const route = useRoute();
const router = useRouter();
const {user, bookclub} = route.params;
const isUserFinishedReadingBook = ref(false);
const reviewPost = ref(null);

let currentlyReadingBook = {};

function showUpdateForm() {
    const dialogRef = overlays.value?.updateOverlay;
    dialogRef?.showModal();
};

function showFinishedReadingForm() {
    const dialogRef = overlays.value.finishedReadingOverlay;
    dialogRef?.showModal(); 
}

/**
 * @load
 * @description – Reruns every time the club loads
 */

// If you are done reading call a different url.
let feedUrl = urls.bookclubs.getClubFeed(route.params.bookclub);
if (props.club.currently_reading_book.is_user_finished_reading) {
    feedUrl = urls.bookclubs.getFinishedClubFeed(route.params.bookclub);
};

const clubFeedPromise = db.get(feedUrl, null, false, (res) => {
    data.value.posts = res.posts;
},
(err) => {
    console.log(err);
});

const clubFeedPromiseFactory = () => db.get(feedUrl, null, false, (res) => {
    data.value.posts = res.posts;
},
(err) => {
    console.log(err);
});

const currentlyReadingPromise = db.get(urls.bookclubs.getCurrentlyReadingForClub(bookclub), null, false, (res) => {
    currentlyReadingBook = res.currently_reading_book;
});

Promise.allSettled([clubFeedPromise, currentlyReadingPromise]).then(() => {
    loaded.value = true;
});



// If you are coming from notifications tab, then load the showUpdateForm, then unwatch watcher.
watch(() => overlays.value.updateOverlay, () => {
    if (route.query['make-update']) {
        showUpdateForm()
    }  
    watch()
}, {immediate: false});


// So users can scroll up and refresh feed. 
function refreshFeed() {
    loaded.value = false;
    Promise.resolve(clubFeedPromiseFactory()).then(() => {
        loaded.value = true;
    });
}


/**
 * @post
 */
function postUpdateForBookClub(update) {
    update = formatUpdateForBookClub(update, route.params.user)

    db.post(urls.bookclubs.createClubUpdate(bookclub), update, false, 
        (res) => {
            console.log(res);
            // Refresh;
            const { dialogRef } = overlays.value.updateOverlay;
            dialogRef?.close();
            createConfetti();
            refreshFeed();
        },
        (err) => {
            console.warn(err);
        },
    );
};


// Allow posting and then closing the overlay.
function postReviewAndFinishReadingCurrentBook(post) {
    post.user = {id: currentUser.value.id }

    if (!post) {
        db.post(
            urls.concatQueryParams(
                urls.bookclubs.postClubReviewAndFinishReading(bookclub, props.club.currently_reading_book.book_club_book_id),
                { no_review: true },
            ), 
            null, 
            false, 
            (res) => {
                isUserFinishedReadingBook.value = true;
            }, (err) => {
                console.error(err);
            }
        );
    } else {   
        db.post(urls.bookclubs.postClubReviewAndFinishReading(bookclub, props.club.currently_reading_book.book_club_book_id), 
            post, 
            false, 
            (res) => {
                isUserFinishedReadingBook.value = true;
            }, 
            (err) => {
                console.error(err);
            }
        );
    };

    const { dialogRef } = overlays.value.finishedReadingOverlay;
    dialogRef?.close();
    createConfetti();
}
</script>