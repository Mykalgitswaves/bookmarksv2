<template>
    <AsyncComponent :promise-factory="loadShelvesPromiseFactory" :subscription-id="BOOKSHELVES_BY_SECTION_SUBSCRIPTION_KEY">
        <template #resolved>
            <div class="bookshelves-main-container ml-0" v-if="shelfType !== 'explore'">
                <Bookshelves
                    :bookshelves="bookshelves"
                    :is_admin="!!(route.params.shelfType === 'created_bookshelves')"
                    :data-loaded="dataLoaded"
                    :is-on-section-page="true"
                >
                    <template v-slot:heading>
                        <h1 class="bookshelf-wrapper-title font-medium fancy">
                            {{ titleMap.get(shelfType, '') }} 
                            
                            <span class="text-indigo-500">
                                {{ bookshelves?.length }}
                            </span>
                        </h1>
                    </template>

                    <template v-if="bookshelves?.length > 0" 
                        v-slot:empty-shelf
                    >
                        <p>You haven't created any bookshelves yet</p>
                    </template>
                </Bookshelves>
            </div>

            <!-- IF You are exploring! -->
            <ExploreBookshelves 
                v-if="shelfType === 'explore'" 
                :bookshelves="bookshelves"
                :user-id="user"
            />

            <Pagination @updated:page="paginationHandler"/>
        </template>
        <template #loading>
            <div class="gradient loading bookshelf"></div>
        </template>
    </AsyncComponent>
    
</template>
<script setup>
import Bookshelves from './bookshelves.vue';
import { useRoute, useRouter } from 'vue-router';
import {ref} from 'vue'
import {urls, navRoutes} from '../../../services/urls';
import { db } from '../../../services/db';
import { PubSub } from '../../../services/pubsub';
import AsyncComponent from '../partials/AsyncComponent.vue';
import ExploreBookshelves from './ExploreBookshelves.vue';

const props = defineProps({
    shelfType: {
        type: String,
        required: true,
    },
});

const BOOKSHELVES_BY_SECTION_SUBSCRIPTION_KEY = 'bookshelves-by-section-get-bookshelves';
// use offset to control how many we see per page or per filter.
const pagination = ref({
    start: 0,
    offset: 10,
});

const route = useRoute();
const router = useRouter();
const { user, shelfType } = route.params;

const urlMap = {
    explore: urls.rtc.getExploreBookshelves(user),
    created_bookshelves: urls.rtc.getBookshelvesCreatedByUser(user),
    member_bookshelves: urls.rtc.getMemberBookshelves(user),
}

const titleMap = {
    created_bookshelves: 'Your created bookshelves',
    member_bookshelves: 'Bookshelves you follow',
    explore: 'Explore bookshelves from your network',
}

// Right after we load, if we are in a weird shelf page, kick people back to a different place.
if (!urlMap[shelfType]) {
    router.push(navRoutes.toBookshelvesMainPage(user));
}

const bookshelves = ref([]);

const loadShelvesPromiseFactory = () => db.get(urlMap[shelfType], 
    {'pagination': [pagination.value.start, pagination.value.start + pagination.value.offset]},
    false, 
    (res) => {
        bookshelves.value = res.bookshelves;
    }
);

function paginationHandler(pageVector) {
    pagination.value.start = pageVector[0];
    pagination.value.offset = pageVector[1];
    PubSub.publish(BOOKSHELVES_BY_SECTION_SUBSCRIPTION_KEY)
}
// END OF NEW CODE
</script>
<style scoped>
.bookshelf-wrapper-title {
  font-size: var(--font-2xl);
  color: var(--slate-800);
}
</style>