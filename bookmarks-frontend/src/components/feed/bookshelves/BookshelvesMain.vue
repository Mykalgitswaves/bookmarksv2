<template>
    <section class="bookshelves-main-container">
        <Bookshelves 
            :bookshelves="currentlyReadingShelf"
            :is_admin="true"
            :is-unique="'currently-reading'"
            :data-loaded="dataLoaded"
        >
            <template v-slot:heading>
                <h1 class="bookshelf-wrapper-title font-medium fancy">
                Currently reading 
                    <span v-if="dataLoaded">
                        <br/>
                        <span class="text-indigo-500 text-sm" v-if="currentlyReadingShelf[0]?.books?.length">
                            {{ currentlyReadingShelf[0]?.books?.length}} books
                        </span>

                        <span v-else class="text-indigo-500 text-sm">
                            No books in this shelf
                        </span>
                    </span>

                    <span v-else class="text-stone-500 text-sm"><br>Loading...</span>
                </h1>
            </template>
        </Bookshelves>

        <div class="bookshelves-divider"></div>

        <Bookshelves :bookshelves="wantToReadBookshelf"
            :is_admin="true"
            :is-unique="'want-to-read'"
            :data-loaded="dataLoaded"
        >
            <template v-slot:heading>
                <h1 class="bookshelf-wrapper-title font-medium fancy">
                Want to read
                    <span v-if="dataLoaded">
                        <br/>
                        <span class="text-indigo-500 text-sm" v-if="wantToReadBookshelf[0]?.books?.length">
                            {{ wantToReadBookshelf[0]?.books?.length}} books
                        </span>

                        <span v-else class="text-indigo-500 text-sm">
                            No books in this shelf
                        </span>
                    </span>

                    <span v-else class="text-stone-500 text-sm"><br>Loading...</span>
                </h1>
            </template>
        </Bookshelves>

        <div class="bookshelves-divider"></div>

        <Bookshelves :bookshelves="bookshelvesCreatedByUser"
            :is_admin="true"
            :data-loaded="dataLoaded"
        >
            <template v-slot:heading>
                <h1 class="bookshelf-wrapper-title font-medium fancy">
                You've created 
                    <span v-if="dataLoaded">
                        <br/>
                        <span class="text-indigo-500 text-sm" v-if="bookshelvesCreatedByUser?.length">
                            {{ bookshelvesCreatedByUser?.length }} bookshelves
                        </span>

                        <span v-else class="text-indigo-500 text-sm">
                            No books in this shelf
                        </span>
                    </span>

                    <!-- Loading text -->
                    <span v-else class="text-stone-500 text-sm"><br>Loading...</span>
                </h1>
            </template>
            
            <template v-if="dataLoaded && !(bookshelvesCreatedByUser.length > 0)" 
                v-slot:empty-shelf
            >
                <p>You haven't created any bookshelves yet</p>
            </template>
        </Bookshelves>


        <div class="bookshelves-divider"></div>

        
        <Bookshelves :bookshelves="[]" :data-loaded="true">
            <template v-slot:heading>
                <h1 class="bookshelf-wrapper-title font-medium fancy">
                    Followed bookshelves
                </h1>
            </template>

            <template v-slot:empty-shelf>
                <p class="nowrap text-sm mt-2">You haven't followed any bookshelves yet</p>
            </template>
        </Bookshelves>

        
        <div class="bookshelves-divider"></div>

        <div>
            <div>
                <h1 class="bookshelf-wrapper-title font-medium fancy mb-2">Explore bookshelves</h1>
   
                <span>
                    <a :href="navRoutes.toBookshelfSectionPage(user, 'explore')" 
                        class="underline text-indigo-500 text-sm"
                    >Find new bookshelves</a>
                </span>
            </div>
        </div>
    </section>
</template>
<script setup>
import Bookshelves from './bookshelves.vue'; 
import { db } from '../../../services/db';
import { urls, navRoutes } from '../../../services/urls';
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const { user } = route.params;
const bookshelvesCreatedByUser = ref([]);
const wantToReadBookshelf = ref(null);
const currentlyReadingShelf = ref(null);
const dataLoaded = ref(false);

async function getBookshelves(){
    const createdByUserPromise = await db.get(urls.rtc.getBookshelvesCreatedByUser(user));
    const wantToReadPromise = await db.get(urls.rtc.getWantToRead(user));
    const currentlyReadingPromise = await db.get(urls.rtc.getCurrentlyReading(user));

    Promise.all([createdByUserPromise, wantToReadPromise, currentlyReadingPromise]).then(([createdByUser, wantToRead, currentlyReading]) => {
        bookshelvesCreatedByUser.value = createdByUser.bookshelves;
        wantToReadBookshelf.value = [wantToRead.bookshelf];
        currentlyReadingShelf.value = [currentlyReading.bookshelf];
        dataLoaded.value = true;
    });
};

onMounted(() => {
    getBookshelves();
});
</script>
<style scoped>

/* Bookshelves */

.bookshelf:hover {
  background-color: var(--stone-100);
}

.bookshelf-wrapper-title {
  font-size: var(--font-2xl);
  color: var(--slate-800);
  line-height: 1;
}

.bookshelves-divider {
    height: 1px;
    width: 100%;
    background-color: var(--stone-100);
    margin-bottom: 14px;
}
</style>