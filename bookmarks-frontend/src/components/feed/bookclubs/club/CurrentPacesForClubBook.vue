<template>
    variable
</template>
<script setup>
import { ref } from 'vue';
import { useRoute } from 'vue-router';
import { db } from '../../../../services/db';
import { urls } from '../../../../services/urls';

const loaded = ref(false);
let currentPaces; 
const route = useRoute();

db.get(urls.bookclubs.getClubPace(route.params.bookclub), null, false, (res) => {
    currentPaces = res.member_paces
}, (err) => {
    console.error(err);
});

</script>