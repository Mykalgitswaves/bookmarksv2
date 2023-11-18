<template>
    <BackBtn/>
    
    <section>
        <div class="book-page-header">
            <div class="book-info-card">
                <img :src="book_img" alt="" class="book-info-card-img">

                <div class="book-info-card-info">
                    <h2 class="text-2xl font-semibold ml-2">{{ book?.title }}</h2>

                    <p>{{ book?.isbn24 }}</p>

                    <p class="ml-2 text-slate-600">
                        <span 
                            v-for="(author, index) in book?.author_names"
                            :key="index"
                        >
                            {{
                                author + commanator(index, book?.author_names?.length) 
                            }}
                        </span>
                        <span v-if="!book.author_names && !book.author_names.length">
                            Not listed...
                        </span>
                    </p>
                </div>
            </div>

            <div class="flex">
                <button 
                    type="button"
                    class=""
                >
                Add to bookshelf
                </button>
            </div>
        </div>
    </section>
</template>

<script setup>
// import SimilarBooks from '@/components/feed/SimilarBooks.vue';
import BackBtn from './partials/back-btn.vue';
import { ref, computed } from 'vue';
import { useRoute } from 'vue-router'
import { db } from '../../services/db';
import { urls } from '../../services/urls';
import { helpersCtrl } from '../../services/helpers';

const route = useRoute();
const { commanator } = helpersCtrl
const book_id = route.params.work;
const book = ref(null);

async function getWorkPage() {
    await db.get(urls.books.getBookPage(book_id), null, true).then((res) => {
        book.value = res.data;
    })
}
getWorkPage()

const book_img = computed(() => (book.value?.small_img_url || book.value?.img_url));

</script>
<style scoped>
    .book-page-header {
        background-color: #f8fafc;
        padding: 15px;
        margin-top: 20px;
    }
    .book-info-card {
        display: flex;
        column-gap: 20px;
        border-radius: 6px;
    }

    .book-info-card-img {
        height: 200px;
        width: auto;
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