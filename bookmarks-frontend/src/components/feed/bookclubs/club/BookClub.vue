<template>
    <section class="section-width section-wrapper"> 
            <div v-if="loaded">
                <BookClubFeed 
                    v-if="currentView === subComponentRoutes.feed" 
                    :club="club"
                />

                <ClubPostCommentsView 
                    v-else-if="currentView === subComponentRoutes.feedCommentsPage"
                />

                <SubThreadView 
                    v-else-if="currentView === subComponentRoutes.feedCommentSubThreadPage"
                />

                <ClubMemberSettingsMain 
                    v-else-if="currentView === subComponentRoutes.settings.manageMembers"
                    :club="club"
                />

                <CurrentlyReadingSettings 
                    v-else-if="currentView === subComponentRoutes.settings.currentlyReading"
                    :club="club"    
                />

                <ClubAfterwords
                    ref="wrappedSection"
                    v-else-if="currentView === subComponentRoutes.wrappedSection"
                    :club="club"
                />
            </div>

            <!-- more loading states -->
            <div v-else class="bookclub-header text-center gradient">
                <h3 class="text-xl fancy text-stone-700">Sit tight, your club is loading...</h3>
            </div>
    </section>

    <!-- <teleport to="main-layout"> -->
        
    <!-- </teleport>     -->
</template>
<script setup>
import { ref, computed, defineAsyncComponent } from 'vue';
import { useRouter, useRoute } from 'vue-router';

// Services
import { db } from '../../../../services/db';
import { navRoutes, urls } from '../../../../services/urls';

// Stores
import {  useCurrentUserStore } from '@/stores/currentUser';

// svg
// import IconSettings from '../../../svg/icon-settings.vue';
// subcomponent views!
const BookClubFeed = defineAsyncComponent(() => import('./BookClubFeed.vue'));
const ClubMemberSettingsMain = defineAsyncComponent(() => import('./invite/ClubMemberSettingsMain.vue'));
const CurrentlyReadingSettings = defineAsyncComponent(() => import('../currently-reading/CurrentlyReadingSettings.vue'));
const ClubPostCommentsView = defineAsyncComponent(() => import('./posts/ClubPostCommentsView.vue'));
const SubThreadView = defineAsyncComponent(() => import('./posts/comments/SubThreadView.vue'));
const ClubAfterwords = defineAsyncComponent(() => import('./afterwords/ClubAfterwords.vue'));


/**
 * ----------------------------------------------------------------------------
 * @constants
 * ----------------------------------------------------------------------------
 */

const route = useRoute();
const router = useRouter();
const { user, bookclub, postId, threadId } = route.params;
const loaded = ref(false);
const wrappedSection = ref(null);

let error;
let club;

/**
 * @update_store
 * @description - Update your js shared state for current user to have the current book clubs relationships reflected on the object.
 */

const store = useCurrentUserStore();
store.getCurrentClubRelationshipsOnUser(user, bookclub);

const subComponentRoutes = {
    feed: 'feed',
    feedCommentsPage: 'feed-comments-page',
    feedCommentSubThreadPage: 'feed-comments-sub-thread-page',
    settings: {
        currentlyReading: 'currently-reading',
        manageMembers: 'manage-members',
    },
    wrappedSection: 'wrapped',
}

const currentView = computed(() => {
    console.log(user, route.params)
    if (route.name === 'clubFeed') {
        console.log('feed')
        return subComponentRoutes.feed;
    } else if (route.name === 'currentlyReading') {
        console.log('currently-reading')
        return subComponentRoutes.settings.currentlyReading;
    } else if (route.name === 'manageMembers') {
        console.log('manage-members')
        return subComponentRoutes.settings.manageMembers;
    } else if (route.name === 'clubCommentPage') {
        console.log('comments page')
        return subComponentRoutes.feedCommentsPage;
    } else if (route.name === 'clubCommentsSubThreadPage') {
        console.log('sub thread baby')
        return subComponentRoutes.feedCommentSubThreadPage;
    } else {
        return subComponentRoutes.feed;
    }
});



/**
 * ----------------------------------------------------------------------------
 * @end_of_constants
 * ----------------------------------------------------------------------------
 */

/**
 * ----------------------------------------------------------------------------
 * @events
 * ----------------------------------------------------------------------------
 */


/**
 * ----------------------------------------------------------------------------
 * @functions
 * ----------------------------------------------------------------------------
 */


async function loadBookClub() {
    db.get(urls.bookclubs.getMinimalClub(bookclub, user), null, false, 
        (res) => {
            console.log('this worked')
            club = res.book_club;
            loaded.value = true;
        },
        (err) => {
            console.log('this failed')
            error = err;
        }
    );
}

/**
 * ----------------------------------------------------------------------------
 * @end_of_functions
 * ----------------------------------------------------------------------------
 */

/**
 * ----------------------------------------------------------------------------
 * @load
 * ----------------------------------------------------------------------------
 */

 loadBookClub();

/**
 * ----------------------------------------------------------------------------
 * @end_of_load
 * ----------------------------------------------------------------------------
 */
</script>
<style>
.bookclub-header {
    background-color: var(--stone-100);
    padding: 20px 40px;
    border-radius: var(--radius-md);
}

.club-main-padding {
    padding: 20px;
}

/* .book-club-nav {
    display: none;
} */

/* @media screen and (min-width: 768px) { */
    .book-club-nav {
        display: flex;
        column-gap: 8px;
        align-items: center;
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-33%);
        width: 100%;
    }
/* } */
</style>