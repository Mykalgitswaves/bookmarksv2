<template>
<div>
        <h1 class="text-4xl fancy text-stone-700 mb-10 mt-10">Bookclubs</h1>

        <div class="bookclubs-list">
            <h2 class="text-2xl fancy text-stone-600">Clubs you've joined</h2>
            
            <div v-if="bookClubsJoinedByCurrentUser?.length" class="mb-5">
            <!-- TODO turn into component like bookshelves -->
            </div>

            <p v-else class="text-lg font-medium text-stone-500 mt-5 mb-5">
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

        <div class="bookclubs-list">
            <h2 class="fancy text-2xl text-stone-600 mb-5">Clubs you own</h2>    
            
            <ul v-if="bookClubsOwnedByCurrentUser?.length">
                <li v-for="club in bookClubsOwnedByCurrentUser">

                </li>
            </ul>

            <p v-else class="text-lg font-medium text-stone-500 mb-5">
                You haven't created any clubs yet.
            </p>
            
            <div class="toolbar">
                <button 
                    class="btn btn-submit small" 
                    @click="router.push(toCreateClubPage(user))"
                >
                    Create club
                </button>
            </div>
        </div>
    </div>
</template>
<script setup>
import { navRoutes } from '../../../../services/urls';
import { useRoute, useRouter } from 'vue-router';
/**
 * @nav_constants
 * @description constants for navigation on the page. 
 */

const { toCreateClubPage } = navRoutes;
const route = useRoute();
const { user } = route.params
const router = useRouter();
/**
 * END OF CONSTANTS 
 */
</script>
<style scoped>
.bookclubs-list {
    padding: 14px; 
    border-radius: var(--radius-md);
    border: 1px solid var(--stone-500);
    margin-top: 14px;
    margin-bottom: 14px;
    
    & .toolbar {
        border-top: 1px solid var(--stone-300);
        padding-top: 14px;
        display: flex;
        align-items: center;
        justify-content: start;
        column-gap: 14px;
    }
}
</style>