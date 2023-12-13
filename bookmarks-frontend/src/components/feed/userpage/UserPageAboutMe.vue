<template>
    <div v-if="data" class="user-about-settings-wrap">
        <h2 v-if="data?.genres?.length" class="text-indigo-600 text-medium">Your favorite genres</h2>

        <div  class="grid-pills settings">
            <div 
                v-for="genre in data?.genres" :key="genre[1]"
                class="border-indigo-300 text-indigo-900 
                    px-2 text-center py-2 rounded-lg border-2 
                    border-solid"    
            >
                {{ genre[0] }}
            </div>
        </div>

        <h2 v-if="data?.authors?.length" class="text-indigo-600 text-medium">Your favorite authors</h2>

        <div 
            v-for="author in data?.authors" :key="author[1]"
            class="border-indigo-300 text-indigo-900 
                px-2 text-center py-2 rounded-lg border-2 
                border-solid"    
        >
            {{ author[0] }}
        </div>
    </div>

    <LoadingIndicatorBook v-else/>
</template>
<script setup>
import { ref, watchEffect } from 'vue';
import { useRoute } from 'vue-router';
import { db } from '../../../services/db';
import { urls } from '../../../services/urls';
import LoadingIndicatorBook from '../partials/LoadingIndicatorBook.vue';

const route = useRoute();
const { user_profile } = route.params;
const data = ref(null);

watchEffect(() => {
    db.get(urls.user.getUserAbout(user_profile)).then((res) => {
        data.value = res.data
    });
});
</script>