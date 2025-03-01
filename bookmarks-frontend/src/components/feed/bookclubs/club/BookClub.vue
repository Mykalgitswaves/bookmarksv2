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
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { db } from '../../../../services/db';
import { navRoutes, urls } from '../../../../services/urls';
// svg
// import IconSettings from '../../../svg/icon-settings.vue';
// subcomponent views!
import BookClubFeed from './BookClubFeed.vue';
import ClubMemberSettingsMain from './invite/ClubMemberSettingsMain.vue';
import CurrentlyReadingSettings from '../currently-reading/CurrentlyReadingSettings.vue';
import ClubPostCommentsView from './posts/ClubPostCommentsView.vue';
import SubThreadView from './posts/comments/SubThreadView.vue';
import ClubAfterwords from './afterwords/ClubAfterwords.vue';

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
    if (route.path === navRoutes.toBookClubFeed(user, bookclub)) {
        console.log('feed')
        return subComponentRoutes.feed;
    } else if (route.path === navRoutes.bookClubSettingsCurrentlyReading(user, bookclub)) {
        console.log('currently-reading')
        return subComponentRoutes.settings.currentlyReading;
    } else if (route.path === navRoutes.bookClubSettingsManageMembersIndex(user, bookclub)) {
        console.log('manage-members')
        return subComponentRoutes.settings.manageMembers;
    } else if (route.path === navRoutes.toBookClubCommentPage(user, bookclub, route.params?.postId)) {
        console.log('comments page')
        return subComponentRoutes.feedCommentsPage;
    } else if (route.path === navRoutes.toSubThreadPage(user, bookclub, postId, threadId)) {
        console.log('sub thread baby')
        return subComponentRoutes.feedCommentSubThreadPage;
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

document.addEventListener


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