<template>
    <div class="bookshelves-main-container ml-0">  
        <Bookshelves :bookshelves="bookshelves"
            :is_admin="!!(route.params.shelfType === 'created_bookshelves')"
            :data-loaded="dataLoaded"
            :is-on-section-page="true"
        >
            <template v-slot:heading>
                <h1 class="bookshelf-wrapper-title font-medium fancy">
                    {{ sectionTitle() }} 
                    
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
</template>
<script setup>
import { ref, onMounted } from 'vue';
import { db } from '../../../services/db';
import { urls } from '../../../services/urls';
import { useRoute } from 'vue-router';
import Bookshelves from './bookshelves.vue';

const props = defineProps({
    shelfType: {
        type: String,
        required: true,
    },
});

const route = useRoute();
const bookshelves = ref([]);
const dataLoaded = ref(false);

const sectionTitle = () => {
    if(route.params.shelfType === 'created_bookshelves'){
        return 'Your created bookshelves';
    } else if(route.params.shelfType === 'member_bookshelves'){
        return 'Bookshelves you follow';
    }
    // Add in more functinoality here as we add in more bookshelf types. 
};


async function getBookshelvesForSection(){
    let url = '';
    if(route.params.shelfType === 'created_bookshelves') {
        url = urls.rtc.getBookshelvesCreatedByUser(route.params.user);
    } else if(route.params.shelfType === 'member_bookshelves') {
        url = urls.rtc.getMemberBookshelves(route.params.user);
    }
    await db.get(url).then((res) => {
        bookshelves.value = res.bookshelves;
        dataLoaded.value = true;
    });
}

onMounted(async () => {
    await getBookshelvesForSection();
});
</script>
<style scoped>
.bookshelf-wrapper-title {
  font-size: var(--font-2xl);
  color: var(--slate-800);
}
</style>