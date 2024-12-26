<template>
    <div class="post-section-wrapper">
        <h1 class="text-3xl text-stone-600 fancy">Bookshelves</h1>

        <TextAlert :variant="TA.info.cls" :is-collapsible="true" id="text-alert" :icon-override="'none'">
            <template #alert-heading>
                More about bookshelves
            </template>
            <template #alert-content>
                <p class="text-xs text-stone-500 italic">
                    Add books to your shelves in order to keep track of what you are reading, want to read, and books you have finished.<br/>
                    Use your own private bookshelves or create custom, public bookshelves to share reading lists with your friends.
                </p>
            </template>
        </TextAlert>

        <div class="bookshelf-filters">
            <TextInput 
                placeholder="search for bookshelves" 
                @updated:modelValue="(value) => searchForBookshelf(value)"
            />

            <RouterLink 
                :to="navRoutes.toBookshelfSectionPage(user, 'explore')" 
                class="ml-auto btn btn-tiny text-indigo-500 text-sm btn-nav"
            >
                Explore bookshelves
            </RouterLink>
        </div>

        <section v-if="searchedBookshelves?.length">
            <h4 class="text-stone-600 text-base fancy mb-5">Searched shelves</h4>

            <!-- Making is_admin false because we dont want to be able to create from  -->
            <Bookshelves
                :bookshelves="searchedBookshelves"
                :is_admin="false"
                :is-unique="false"
                :data-loaded="true"
            />
        </section>

        <div class="bookshelves-divider"></div>

        <!-- Created shelves -->
        <section class="bookshelves-main-container">
            <h4 class="text-stone-600 text-base fancy mb-5">Preset shelves</h4>

            <AsyncComponent :promises="[presetShelvesPromise()]" v-if="!activeFilters['preset']">
                <template #resolved>

                    <Bookshelves
                        v-for="(bookshelf, index) in presetBookshelves"
                        :key="index"
                        :bookshelves="bookshelf.shelf"
                        :is_admin="bookshelf.admin"
                        :is-unique="bookshelf.isUnique"
                        :data-loaded="true"
                    />
                </template>

                <template #loading>
                    <div class="loading gradient bookshelf"></div>
                    <div class="loading gradient bookshelf"></div>
                    <div class="loading gradient bookshelf"></div>
                </template>
            </AsyncComponent>

            <h4 v-else class="fancy text-sm text-stone-500">🪄 Filtering out preset shelves...✨</h4>
        </section>

        <div class="bookshelves-divider mt-5"></div>

        <!-- Created shelves -->
        <section class="bookshelves-main-container">
            <h4 class="text-stone-600 text-base fancy mb-5">Created shelves</h4>
            <AsyncComponent :promises="[bookShelvesCreatedByUserFactory()]" v-if="!activeFilters['created']">
                <template #resolved>
                    <!-- Only show the first three -->
                    <Bookshelves
                        :bookshelves="createdShelves"
                        :is_admin="true"
                        :is-preview="true"
                        :data-loaded="true"
                    />
                </template>

                <template #loading>
                    <div class="loading gradient bookshelf"></div>
                    <div class="loading gradient bookshelf"></div>
                    <div class="loading gradient bookshelf"></div>
                </template>
            </AsyncComponent>

            <h4 v-else class="fancy text-sm text-stone-500">🪄 Filtering out created shelves...✨</h4>
        </section>

        <div class="bookshelves-divider"></div>

        <!-- Created shelves -->
        <section class="bookshelves-main-container">
            <h4 class="text-stone-600 text-base fancy mb-5">Joined shelves</h4>
            <AsyncComponent :promises="[memberShelvesPromiseFactory()]" v-if="!activeFilters['joined']">
                <template #resolved>
                    <!-- Only show the first three -->
                    <Bookshelves
                        v-if="joinedBookshelves.length"
                        :bookshelves="joinedBookshelves"
                        :is_admin="false"
                        :is-preview="true"
                        :data-loaded="true"
                    />

                    <div v-else>
                        <p class="text-stone-600 text-sm">You havent joined any bookshelves</p>

                        <RouterLink 
                            :to="navRoutes.toBookshelfSectionPage(user, 'explore')" 
                            class="underline text-indigo-500 text-sm"
                        >
                            Find new bookshelves
                        </RouterLink>
                    </div>
                </template>

                <template #loading>
                    <div class="loading gradient bookshelf"></div>
                    <div class="loading gradient bookshelf"></div>
                    <div class="loading gradient bookshelf"></div>
                </template>
            </AsyncComponent>

            <h4 v-else class="fancy text-sm text-stone-500">🪄 Filtering out created shelves...✨</h4>
        </section>
    </div>
</template>
<script setup>
import Bookshelves from './bookshelves.vue'; 
import { db } from '../../../services/db';
import { urls, navRoutes } from '../../../services/urls';
import { ref } from 'vue';
import { useRoute } from 'vue-router';
import TextAlert from '../partials/textAlert/TextAlert.vue';
import { TEXT_ALERT as TA } from '../partials/textAlert/textAlert';
import AsyncComponent from '../partials/AsyncComponent.vue';
import TextInput from '../partials/TextInput.vue';

const route = useRoute();
const { user } = route.params;
/**
 * @SHELVES_CONSTANTS
 */
const presetBookshelves = ref({
    currentlyReading: {
        shelf: null,
        isUnique: 'currently-reading',
        admin: true,
    },
    wantToRead: {
        shelf: null,
        isUnique: 'want-to-read',
        admin: true,
    },
});

// Bookshelf refs.
const createdShelves = ref([]);
const exploreShelves = ref([]);
const joinedBookshelves = ref([])
const searchedBookshelves = ref([]);

/**
 * @END_OF_SHELVES
 */

// Filters
const activeFilters = ref({
    preset: false,
    joined: false,
    created: false,
});

/**
 * ----------------------------------------------------------------------------
 * @FACTORIES
 * ----------------------------------------------------------------------------
 */
const presetFactories = {
    wantToRead: () => db.get(
        urls.rtc.getWantToRead(user), 
        null, 
        false, 
        (res) => {
            presetBookshelves.value.wantToRead.shelf = [res.bookshelf];
        }
    ),
    currentlyReading: () => db.get(
        urls.rtc.getCurrentlyReading(user), 
        null, 
        false, 
        (res) => {
            presetBookshelves.value.currentlyReading.shelf = [res.bookshelf];
        }
    ),
}

const bookShelvesCreatedByUserFactory = () => db.get(
    urls.rtc.getBookshelvesCreatedByUser(user), 
    null, 
    false, 
    (res) => {
        createdShelves.value = res.bookshelves
        console.log(createdShelves.value, 'created shelves')
    }
);

const memberShelvesPromiseFactory = () => db.get(urls.rtc.getMemberBookshelves(user), {pagination: [0, 3]}, false, (res) => {
    console.log('joined', res)
    joinedBookshelves.value = res.bookshelves;
}); 

const exploreBookshelves = () => db.get(urls.rtc.getExploreBookshelves(user), 
    null, 
    false,
    (res) => {
        exploreShelves.value = res.bookshelves;
    }
);


async function presetShelvesPromise() {
    const promises = Object.values(presetFactories).map((factory) => factory())
    return Promise.allSettled(promises).then(() => {
        return true
    });
};

async function searchForBookshelf(value) {
    db.get(urls.search.bookshelf(value), null, false, (res) => {
        searchedBookshelves.value = res.data;
    });
}
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

.bookshelf-filters {
    margin-top: 12px;
    padding: 8px 20px;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(12ch, 1fr));
    column-gap: 8px;
    row-gap: 8px;
}

.bookshelf-filter {
    border-radius: 4px; 
    border: 1px solid var(--stone-100);
    background-color: var(--stone-100);
    color: var(--indigo-500);
    font-family: var(--fancy-script);
    font-size: var(--font-sm);
    padding: 4px;
}

.bookshelf-filter.active {
    border-color: var(--indigo-600);
    background-color: var(--indigo-50);
}

.bookshelf.loading {
    width: 100%;
    height: 50px;
    border-radius: 4px;
}

#text-alert {
    margin-left: unset;
    margin-top: 10px;
}
</style>