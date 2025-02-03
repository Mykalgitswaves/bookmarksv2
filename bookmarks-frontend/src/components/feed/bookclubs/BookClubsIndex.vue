<template>
    <section>
        <RouterView></RouterView>
    </section>

    <div class="mobile-menu-spacer sm:hidden"></div>
</template>
<script setup>
import BackBtn from './../partials/back-btn.vue';
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { navRoutes } from '../../../services/urls';
const route = useRoute();

const showBackButton = computed(() => {
    const pathForClub = navRoutes.toBookClubFeed(route.params.user, route.params.bookclub)
    const currentPath = route.fullPath;
    return !currentPath.includes(pathForClub);
})
</script>
<style></style>