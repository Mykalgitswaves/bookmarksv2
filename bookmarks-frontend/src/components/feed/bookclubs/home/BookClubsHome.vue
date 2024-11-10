<template>
    <div class="">
        <h1 class="text-4xl fancy text-stone-700 mb-10 mt-10 ml_20_px">Bookclubs</h1>
        <div class="bookclubs">
            <h2 class="text-2xl fancy text-stone-600">Clubs you've joined</h2>

            <div v-if="loaded">
                
                <!-- TODO turn into component like bookshelves -->
                <p class="text-lg font-medium text-stone-500 mt-5 mb-5">
                    You haven't joined any clubs yet.
                </p>

                <div class="toolbar" v-if="bookClubsJoinedByCurrentUser?.length">
                    <!-- todo: add modal for viewing all clubs. -->
                    <button 
                        type="button" 
                        class="btn btn-ghost small"
                    >View all bookclubs</button>
                </div>
            </div>
        </div>

        <div class="bookclubs">
            <h2 class="fancy text-2xl text-stone-600 mb-5">Clubs you own</h2>  

            <AsyncComponent :promises="[clubsPromise]">
                <template #resolved>
                    <div v-if="bookClubsOwnedByCurrentUser?.length" class="mb-5 mt-5 bookclubs-list">
                        <BookClubPreview 
                            v-for="bookclub in bookClubsOwnedByCurrentUser"
                            :bookclub="bookclub"
                            :user="user"
                        />
                    </div>

                    <!-- loading -->
                    <p v-else>
                        You haven't created any clubs yet.    
                    </p>

                    <div class="toolbar">
                        <button class="btn btn-submit small" 
                            @click="router.push(toCreateClubPage(user))"
                        >
                            Create club
                        </button>
                    </div>
                </template>

                <template #loading>
                    <LoadingCard />
                </template>
            </AsyncComponent>
        </div>
    </div>
</template>
<script setup>
import { db } from '../../../../services/db';
import { urls } from '../../../../services/urls';
import { navRoutes } from '../../../../services/urls';
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import BookClubPreview from './BookClubPreview.vue';
import AsyncComponent from '../../partials/AsyncComponent.vue';
import LoadingCard from '../../../shared/LoadingCard.vue';
/**
 * ----------------------------------------------------------------------------
 * @constants
 * @description constants for navigation on the page. 
 * ----------------------------------------------------------------------------
 */

const { toCreateClubPage } = navRoutes;
const route = useRoute();
const { user } = route.params
const router = useRouter();

const loaded = ref(false);
let bookClubsOwnedByCurrentUser;
let errors;

/**
 * ----------------------------------------------------------------------------
 * END OF CONSTANTS 
 * ----------------------------------------------------------------------------
 */

/**
 * ----------------------------------------------------------------------------
 * @promises
 * @loadClubsCreatedByUser
 * ----------------------------------------------------------------------------
 */

const clubsPromise = db.get(urls.bookclubs.getClubsOwnedByUser(user), null, false, 
    (res) => {
        bookClubsOwnedByCurrentUser = res.bookclubs;
        loaded.value = true;
    },
    (err) => {
        errors = err;
        loaded.value = true;
    }
);

/**
 * ----------------------------------------------------------------------------
 * @end_of_function_definitions
 * ----------------------------------------------------------------------------
 */

</script>
<style scoped>

.bookclubs {
    padding: 14px; 
    border-radius: var(--radius-md);
    border: 1px solid var(--stone-300);
    max-width: 768px;
    margin-top: 14px;
    margin-bottom: 14px;
    margin-left: 40px;
    margin-right: 40px;
    min-height: 100px;

    & .toolbar {
        border-top: 1px solid var(--stone-300);
        padding-top: 14px;
        display: flex;
        align-items: center;
        justify-content: start;
        column-gap: 14px;
    }

    @starting-style {
        .bookclubs-list {
            opacity: 0;
        }
    }

    .bookclubs-list {
        display: grid;
        grid-template-columns: 1fr;
        column-gap: 20px;
        row-gap: 20px;
        transition: 250ms all ease; 
        & * {
            flex-basis: 40%;
        }
    }
}

.ml_20_px {
    margin-left: 20px;
}

.loading-card-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    column-gap: 40px;
}


</style>