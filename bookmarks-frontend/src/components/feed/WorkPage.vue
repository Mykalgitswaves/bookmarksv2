<template>
    <section class="section-wrapper">
        <div class="book-page-header">
            <div class="book-info-card">
                
                    <img v-if="book_img" :src="book_img" alt="" class="book-info-card-img">

                    <div v-else class="transition book-info-card-img">
                        <LoadingCard />
                    </div>

                <div class="book-info-card-info">
                    <div>
                        <h2 class="text-2xl font-semibold ml-2 fancy text-stone-600">{{ book?.title || 'Loading' }}</h2>
                        <p class="ml-2 italic text-stone-500">ISBN: {{ book?.isbn13 || 'Not found' }}</p>
                    </div>

                    <p class="b-i-c-i-authors" 
                        v-if="book?.author_names && book?.author_names?.length"
                    >
                        <span 
                            v-for="(author, index) in book?.author_names"
                            :key="index"
                        >
                            Written by
                            {{
                                author + commanator(index, book?.author_names?.length) 
                            }}
                        </span>
                    </p>
                    <p class="b-i-c-i-authors" 
                        v-if="!book?.author_names || !book?.author_names.length"
                    >
                       Author not found
                    </p>
                </div>
            </div>

            <div class="book-page-toolbar">
                <button 
                    type="button"
                    class="btn btn-ghost btn-icon"
                    @click="showOverlay(overlayRef)"
                >
                    <IconPlus/>
                    Add to bookshelf
                </button>

                <Overlay ref="overlayRef">
                    <template #overlay-main>
                        <AsyncComponent :promises="[loadedPromise]">
                            <template #resolved>
                                <div v-for="bookshelf in bookshelves">
                                    {{ bookshelf.title }}
                                </div>
                            </template>

                            <template #loading>
                                <div></div>
                            </template>
                        </AsyncComponent>
                    </template>
                </Overlay>

                <div class="btn-relative">
                    <button 
                        type="button"
                        class="btn btn-icon btn-ghost"
                        @click="filterPopout = !filterPopout"
                    >
                        <IconAddReview/>
                        Make a post
                    </button>

                    <div 
                        v-if="filterPopout" 
                        class="popout-flyout shadow-lg"
                    >
                        <button 
                            type="button" 
                            v-for="(option, index) in postOptions"
                            :key="index"
                            @click="router.push(mapping[option])"  
                        >
                            {{ option }}
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="book?.description" class="book-page-description">
            <span class="fancy text-base bold">Description: &nbsp;</span>
            <span v-html="book?.description"></span>
        </div>
    </section>
</template>

<script setup>
// import SimilarBooks from '@/components/feed/SimilarBooks.vue';
import { ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router'
import { db } from '../../services/db';
import { urls } from '../../services/urls';
import { helpersCtrl } from '../../services/helpers';
import IconPlus from '../svg/icon-plus.vue';
import LoadingCard from '../shared/LoadingCard.vue'
import IconAddReview from '../svg/icon-add-post.vue';
import Overlay from './partials/overlay/Overlay.vue';
import { showOverlay } from './partials/overlay/overlay-service.js';
import AsyncComponent from './partials/AsyncComponent.vue';

const route = useRoute();
const router = useRouter();
const { commanator } = helpersCtrl;
const { user, work } = route.params;
const book_id = route.params.version ? route.params.version : route.params.work;
const overlayRef = ref(null);
const book = ref(null);
const filterPopout = ref(false);

let bookshelves = [];

async function getWorkPage() {
    await db.get(urls.books.getBookPage(book_id), null, true).then((res) => {
        book.value = res.data;
    })
}

getWorkPage()

const book_img = computed(() => (book.value?.small_img_url || book.value?.img_url));
const postOptions = ["review", "update", "comparison"];

const mapping = {
  "review": `/feed/${user}/create/review/review/work/${work}`,
  "update": `/feed/${user}/create/review/update/work/${work}`,
  "comparison": `/feed/${user}/create/review/comparison/work/${work}`,
};

const memberBookshelvesPromise = db.get(urls.rtc.getMemberBookshelves(user), null, false, 
    (res) => {
        bookshelves.push(...res.bookshelves);
    }, (err) => {
        console.log(err);
    }
);

const getBookshelvesCreatedByUserPromise = db.get(urls.rtc.getBookshelvesCreatedByUser(user), null, false, 
    (res) => {
        bookshelves.push(...res.bookshelves);
    }, (err) => {
        console.log(err);
    }
);

const loadedPromise = Promise.all([memberBookshelvesPromise, getBookshelvesCreatedByUserPromise])

</script>
<style scoped>
    .section-wrapper {
        margin-left: auto;
        margin-right: auto;
    }

    .book-page-header {
        background-color: #fff;
        border: 1px solid var(--stone-200); 
        border-radius: 6px;
        padding: 15px;
        margin-top: 20px;
        max-width: 880px;
        width: 100%;
    }
    .book-info-card {
        display: flex;
        column-gap: 20px;
    }

    .book-page-toolbar {
        margin-top: 20px;
        display: flex;
        column-gap: 20px;
    }

    .b-p-t-btn {
        display: flex;
        align-items: center;
        padding: 8px 25px;
        column-gap: 6px;
        font-size: 14px;
        background-color: #3730a3;
        color: #fff;
        border-radius: 4px;
        transition: 250ms ease;
    }

    .b-p-t-btn.add {
        background-color: #f8fafc;
        color: #3730a3;
        border: 1px solid #3730a3;
        position: relative;
    }

    .b-i-c-i-authors {
        align-self: end;
        font-family: var(--fancy-script);
    }

    .book-info-card-img {
        height: 200px;
        width: 161px;
        transition: all 0.2s ease-out;
        border-radius: 4px;
    }

    .book-info-card-img:hover {
        transform: translateY(-5%) rotateX(15deg) translateZ(0);
        box-shadow: 2px 35px 32px -8px rgba(0, 0, 0, 0.25);
        -webkit-box-shadow: 2px 35px 32px -8px rgba(0, 0, 0, 0.25);
        -moz-box-shadow: 2px 35px 32px -8px rgba(0, 0, 0, 0.25);
    }

    .book-info-card-info {
        display: grid;
        grid-template-columns: 1fr;
        row-gap: 12px;
    }

    .book-page-description {
        width: 100%;
        max-width: 880px;
        padding: 8px;
        margin-top: 20px;
        color: var(--stone-600);
    }

    /* Animations */

    .work-page-enter-active,
    .work-page-leave-active {
        transform: 0 45px;
        transition: opacity 0.5s ease-out;
    }

    .work-page-enter-from,
    .work-page-leave-to {
        opacity: 0;
    }

    .bookloaded-enter-active, .bookloaded-leave-active {
        transition: all .25s ease;
    }

    .bookloaded-enter-from, .bookloaded-leave-to {
        opacity: 1;
    }
</style>