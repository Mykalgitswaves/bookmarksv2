<template>
    <BackBtn/>
    
    <section>
        <div class="book-info-card">
            <img :src="book?.img_url" alt="" class="book-info-card-img">

            <div class="book-info-card-info">
                <h2>{{ book?.title }}</h2>

                <p>{{ book?.isbn24[0] }}</p>

                <p>
                    <span 
                        v-for="(author, index) in book?.author_names"
                        :key="index"
                    >
                        {{ 
                            author + commanator(index, book?.author_names?.length) 
                        }}
                    </span>
                </p>
            </div>
        </div>
    </section>
</template>

<script setup>
// import SimilarBooks from '@/components/feed/SimilarBooks.vue';
import BackBtn from './partials/back-btn.vue';
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router'
import { db } from '../../services/db';
import { urls } from '../../services/urls';
import { helpersCtrl } from '../../services/helpers';

const router = useRouter();
const route = useRoute();
const { commanator } = helpersCtrl
const book_id = route.params.work;
const book = ref(null);

function backToFeed() {
    return router.push(`/feed/${route.params.user}/all`)
};

async function getWorkPage() {
    await db.get(urls.books.getBookPage(book_id), null, true).then((res) => {
        book.value = res.data;
    })
}
getWorkPage()

</script>
<style scoped>
    .book-info-card {
        display: flex;
        column-gap: 20px;
    }

    .book-info-card-info {
        display: grid;
        row-gap: 12px;
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