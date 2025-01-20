<template>
    <main>
        <section v-if="loaded && authenticated">

        </section>
        <section v-else>

        </section>
    </main>
</template>
<script setup>
import {ref} from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { db } from '../../services/db';
import { urls } from '../../services/urls';

let data = {};
let authenticated = false;
const loaded = ref(false);
const route = useRoute();

// TODO: Finish this shit after bookclubs.
db.get(
    urls.bookclubs.loadClubDataForInvite(route.params.invite), 
    null, false, 
    (res) => {

    }, () => {

    }
);
</script>