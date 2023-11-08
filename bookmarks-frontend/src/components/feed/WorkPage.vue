<template>
    <section>
        what up doofas
    </section>
</template>

<script setup>
// import SimilarBooks from '@/components/feed/SimilarBooks.vue';
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router'
import { db } from '../../services/db';
import { urls } from '../../services/urls';

const router = useRouter();
const route = useRoute();

const book_id = route.params.work;
const book = ref(null);

function backToFeed() {
    return router.push(`/feed/${route.params.user}/all`)
};

async function getWorkPage() {
    await db.get(urls.reviews.getBookPage(book_id), null, true);
}
getWorkPage()

</script>
<style scoped>
    .works-wrapper {
        min-height: 250px;
        border-radius: .3rem;
        padding: 1rem;
        max-width: 1000px;
        width: 60vw;
        min-width: 300px;
    }

    .placeholder {
        height: 146px;
        width: 98px;
        background-color: #1e1e1e;
        border-radius: .25rem;
    }

    .work-page-enter-active,
    .work-page-leave-active {
        transform: 0 45px;
        transition: opacity 0.5s ease-out;
    }

    .work-page-enter-from,
    .work-page-leave-to {
        opacity: 0;
    }
</style>