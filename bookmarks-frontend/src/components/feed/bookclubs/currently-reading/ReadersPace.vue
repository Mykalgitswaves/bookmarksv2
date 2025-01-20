<template>
    <div class="club-pace" v-if="loaded">

    </div>
    
    <div v-else class="gradient fancy text-center text-xl loading-box">
        Loading
    </div>
</template>
<script setup>
import { urls } from '../../../../services/urls';
import { db } from '../../../../services/db';
import { useRoute } from 'vue-router';
import { ref } from 'vue';

defineProps({
    book: {
        type: Object,
        required: true,
    }
});
const loaded = ref(false);
let clubPace = null;
const route = useRoute();

const getPacePromise = db.get(
    urls.bookclubs.getPaceForReadersInClub(route.params.bookclub), 
    null,
    false, 
    (res) => {
        console.log(res)        
        clubPace = res.club_pace;
        loaded.value = true;
    }, 
    (err) => {
        console.log(err)
        loaded.value = true;
    }
);
function getPaceForReadersInClub() {
    loaded.value = false;
    Promise.resolve(getPacePromise);
};

getPaceForReadersInClub();
</script>
<style scoped>

</style>