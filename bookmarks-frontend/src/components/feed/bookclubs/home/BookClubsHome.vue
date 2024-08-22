<template>
<div>
        <h1 class="fancy text-4xl text-stone-600">Bookclubs</h1>
        <div>
            <h2 class="fancy text-2xl text-stone-500">Clubs you've joined</h2>
            <div v-if="clubData?.joinedClubs?.length">
            <!-- TODO turn into component like bookshelves -->
            </div>

            <p v-else>
                you haven't joined any clubs yet
            </p>
        </div>

        <div>
            <h2 class="fancy text-2xl text-stone-500">Clubs you own</h2>    

            <div class="toolbar">

                <button class="btn btn-submit small" @click="router.push(toCreateClubPage(user))">
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