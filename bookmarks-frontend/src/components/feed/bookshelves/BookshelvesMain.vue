<template>
    <div class="bookshelves-main-container">
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
                <p>You haven't followed any bookshelves yet</p>
            </template>
        </Bookshelves>

        <div>
            <h1 class="bookshelf-wrapper-title font-medium fancy">Explore bookshelves</h1>

            <a :href="navRoutes.toBookshelfSectionPage(user, 'explore')" class="underline text-indigo-500">Find new bookshelves</a>
        </div>
    </div>
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
const dataLoaded = ref(false);

async function getBookshelves(){
    await db.get(urls.rtc.getBookshelvesCreatedByUser(user)).then((res) => {
        dataLoaded.value = true;
        bookshelvesCreatedByUser.value = res.bookshelves;
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