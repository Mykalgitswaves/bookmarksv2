<template>
    <section class="bookshelves-main-container">
        <Bookshelves :bookshelves="wantToReadBookshelf"
            :is_admin="true"
            :is-unique="'want-to-read'"
            :data-loaded="dataLoaded"
        >
            <template v-slot:heading>
                <h1 class="bookshelf-wrapper-title font-medium fancy">Want to read 
                    <span class="text-indigo-500">
                        {{ wantToReadBookshelf?.books?.length }}
                    </span>
                </h1>
            </template>
        </Bookshelves>

        <Bookshelves :bookshelves="bookshelvesCreatedByUser"
            :is_admin="true"
            :data-loaded="dataLoaded"
        >
            <template v-slot:heading>
                <h1 class="bookshelf-wrapper-title font-medium fancy">Your bookshelves 
                    <span class="text-indigo-500">
                        {{ bookshelvesCreatedByUser?.length }}
                    </span>
                </h1>
            </template>
            
            <template v-if="dataLoaded && !(bookshelvesCreatedByUser.length > 0)" 
                v-slot:empty-shelf
            >
                <p>You haven't created any bookshelves yet</p>
            </template>
        </Bookshelves>

        <Bookshelves :bookshelves="[]" :data-loaded="true">
            <template v-slot:heading>
                <h1 class="bookshelf-wrapper-title font-medium fancy">Followed bookshelves</h1>
            </template>

            <template v-slot:empty-shelf>
                <p class="nowrap">You haven't followed any bookshelves yet</p>
            </template>
        </Bookshelves>

        <div>
            <div class="pb-5">
                <h1 class="bookshelf-wrapper-title font-medium fancy pb-5">Explore bookshelves</h1>
            </div>
            <div class="pt-5">
                <a :href="navRoutes.toBookshelfSectionPage(user, 'explore')" class="underline text-indigo-500">Find new bookshelves</a>
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
const dataLoaded = ref(false);

async function getBookshelves(){
    const createdByUserPromise = await db.get(urls.rtc.getBookshelvesCreatedByUser(user));
    const wantToReadPromise = await db.get(urls.rtc.getWantToRead(user));

    Promise.all([createdByUserPromise, wantToReadPromise]).then(([createdByUser, wantToRead]) => {
        bookshelvesCreatedByUser.value = createdByUser.bookshelves;
        wantToReadBookshelf.value = [wantToRead.bookshelf];
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
}
</style>