<template>
    <Bookshelves
        :bookshelves="bookshelvesCreatedByUser"
        :is_admin="true"
    >
        <template v-slot:heading>
            <h1 class="title font-medium fancy">Your bookshelves 
                <span class="text-indigo-500">
                    {{ bookshelvesCreatedByUser?.length }}
                </span>
            </h1>
        </template>
        
        <template v-slot:empty-shelf>
            <p>You haven't created any bookshelves yet</p>
        </template>
    </Bookshelves>

    <Bookshelves :bookshelves="[]">
        <template v-slot:heading>
            <h1 class="title font-medium fancy">Liked bookshelves</h1>
        </template>

        <template v-slot:empty-shelf>
            <p>You haven't liked any bookshelves yet</p>
        </template>
    </Bookshelves>
</template>
<script setup>
    import Bookshelves from './bookshelves.vue'; 
    import { db } from '../../../services/db';
    import { urls } from '../../../services/urls';
    import { ref, onMounted } from 'vue';
    import { useRoute } from 'vue-router';

    const route = useRoute();
    const { user } = route.params;
    const bookshelvesCreatedByUser = ref([]);

    async function getBookshelves(){
        await db.get(urls.rtc.getBookshelvesCreatedByUser(user)).then((res) => {
            bookshelvesCreatedByUser.value = res.bookshelves;
            console.log(res);
        });
    }

    onMounted(() => {
        getBookshelves();
    });
</script>
<style scoped>
.bookshelf:hover {
    background-color: var(--stone-100);
}

.title {
    font-size: var(--font-2xl);
    color: var(--slate-800);
}
</style>