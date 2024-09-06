<template>
    <section v-if="loaded" class="mt-10">   
        <div class="bookclub-header flex justify-between items-start">
            <div>
                <h1 class="text-3xl fancy text-stone-700">
                    {{ club.book_club_name }}
                </h1>
                
                <p class="text-stone-500 mt-5">
                    {{ club.description || 'Add a description for your book club' }}    
                </p>
            </div>

            <button type="button" class="pt-5 text-indigo-400">
                <span class="visually-hidden">Settings</span>
                <IconSettings />
            </button>
        </div>
        <div class="club-main">
            <CurrentlyReadingBook :currently-reading-book="club.currently_reading_book"/>
        </div>

        <div class="club-nav">

        </div>
    </section>
    <section v-else class="mt-10">
        <div class="bookclub-header text-center">
            <h3 class="text-xl fancy text-stone-700">Sit tight, your club is loading...</h3>
        </div>
    </section>
</template>
<script setup>
import { ref } from 'vue';
import { useRoute } from 'vue-router';
import { db } from '../../../../services/db';
import { urls } from '../../../../services/urls';
import CurrentlyReadingBook from './CurrentlyReadingBook.vue';
// svg
import IconSettings from '../../../svg/icon-settings.vue';

/**
 * ----------------------------------------------------------------------------
 * @constants
 * ----------------------------------------------------------------------------
 */

const route = useRoute();
const { user, bookclub } = route.params;
const loaded = ref(false);
let error;
let club;

/**
 * ----------------------------------------------------------------------------
 * @end_of_constants
 * ----------------------------------------------------------------------------
 */



/**
 * ----------------------------------------------------------------------------
 * @functions
 * ----------------------------------------------------------------------------
 */


async function loadBookClub() {
    const clubPromise = db.get(urls.bookclubs.getMinimalClub(bookclub, user), null, false, 
        (res) => {
            club = res.book_club;
        },
        (err) => {
            error = err;
        }
    );

    Promise.all([clubPromise]).then(() => {
        loaded.value = true;
    });
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
 * @load
 * ----------------------------------------------------------------------------
 */
</script>
<style scoped>
.bookclub-header {
    background-color: var(--stone-100);
    padding: 20px 40px;
    border-radius: var(--radius-md);
}

</style>