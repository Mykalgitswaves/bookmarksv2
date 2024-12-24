<template>
    <h1 class="work-feed-heading">Currently Reading
        <br><span class="text-sm">Books in your currently reading bookshelf</span>
    </h1>
        <!-- If loaded -->
    <AsyncComponent :promises="[currentlyReadingBookClub]">
        <template #resolved>
            <div class="currently-reading" v-if="books.length">
                <div class="currently-reading-book" 
                    v-for="book in books" 
                    :key="book.id"   
                    role="button" 
                    @click="showCurrentlyReadingBookOverlay(book)"
                >
                    <img class="book-img" :src="book.small_img_url"/>

                    <h4 class="book-title text-stone-500">{{ truncateText(book.title, 64) }}</h4>
                    
                    <div class="book-metadata">
                        <p class="progress">{{ `${book.current_page} / ${book.total_pages}` }}</p>
                    </div>
                </div>
            </div>

            <Overlay :ref="(ref) => currentlyReadingDialogRef = ref?.dialogRef">
                <template #overlay-main>
                    <CreateUpdateForm :book="selectedCurrentlyReadingBook" 
                        @post-update="(update) => postUpdateForCurrentlyReading(update)"  
                    />
                </template>
            </Overlay>
        </template>

        <template #loading>
            <!-- IF loading -->
            <div class="currently-reading">
                <div class="currently-reading-book loading">
                    <div class="book-img loading gradient"></div>
                </div>

                <div class="currently-reading-book loading">
                    <div class="book-img loading gradient"></div>
                </div>

                <div class="currently-reading-book loading">
                    <div class="book-img loading gradient"></div>
                </div>

                <div class="currently-reading-book loading">
                    <div class="book-img loading gradient"></div>
                </div>
            </div>
        </template>
    </AsyncComponent>
</template>
<script setup>
import { db } from '../../services/db';
import { urls } from '../../services/urls';
import { ref } from 'vue';
import { useRoute } from 'vue-router';
import { truncateText } from '../../services/helpers';
import { formatUpdateForBookClub } from './bookclubs/bookClubService';
import { helpersCtrl } from '../../services/helpers';
import AsyncComponent from './partials/AsyncComponent.vue';
import Overlay from './partials/overlay/Overlay.vue';
import CreateUpdateForm from './createPosts/update/createUpdateForm.vue'; 

const route = useRoute();
const { user } = route.params;
let books = [];
let bookshelf; 
const selectedCurrentlyReadingBook = ref({});
const updateRef = ref({});

const currentlyReadingBookClub = db.get(urls.rtc.getCurrentlyReadingForFeed(user), null, false, 
    (res) => {
        bookshelf = res.bookshelf;
        books = res.bookshelf.books;
        console.log(res)
    }, 
    (err) => {
        console.error(err);
});

const currentlyReadingDialogRef = ref(null);

function showCurrentlyReadingBookOverlay(book) {
    Object.assign(selectedCurrentlyReadingBook.value, book);
    currentlyReadingDialogRef.value?.showModal();
}

function postUpdateForCurrentlyReading(update) {
    console.log(update);
    let payload = helpersCtrl.formatUpdateData(update)
    console.log(update);
    db.post(urls.reviews.update, payload, false, 
        (res) => {
            // Refresh;
            console.log(res)
            currentlyReadingDialogRef?.close();
        },
        (err) => {
            console.warn(err);
        },
    );
};
</script>
<style scoped lang="scss">
    .currently-reading {
        --x-axis-offset: 24px;
        --height: fit-content;
        @media screen and (max-width: 768px) {
            --x-axis-offset: 14px;
        }

        margin-top: var(--margin-sm);
        margin-bottom: var(--margin-sm);
        margin-left: auto;
        margin-right: auto;
        display: flex;
        column-gap: var(--margin-md);
        justify-content: start;
        height: var(--height);
        overflow-x: scroll;
        overflow-y: visible;
        padding-left: var(--x-axis-offset);
        transition: var(--transition-short);
        -ms-overflow-style: none;  /* IE and Edge */
        scrollbar-width: none;
        border: 1px solid var(--stone-200);
        border-radius: var(--radius-md);
    }

    .currently-reading::-webkit-scrollbar {
        display: none;
    }

    .currently-reading-book {
        --min-width-cr-card: 300px;
        min-width: var(--min-width-cr-card);
        font-family: var(--fancy-script);
        text-align: center;
        position: relative;
        border: 1px solid var(--surface-primary);
        background-color: var(--surface-primary);
        padding: 10px;

        .book-metadata {
            display: flex;
            align-items: start;
            justify-content: space-between;
            padding-left: var(--margin-sm);
            padding-right: var(--margin-sm);
            
            .book-title {
                font-size: var(--font-xl);
            }

            .progress {
                color: var(--indigo-700);
                font-weight: 600;
                position: absolute;
                top: 10px;
                left: 10px;
            }
        }

        .book-img {
            border-radius: var(--radius-md);
            width: 100%;
            height: 240px;
            object-fit: scale-down;
            margin-bottom: 8px;
            border: 4px solid var(--hover-container-gradient);

            &.loading{  
                background-color: var(--stone-200);
                height: 300px;
            }
        }
    }

    .currently-reading-book:not(:has(.gradient)):hover {
        background-color: var(--stone-50);
        border-radius: var(--radius-md);
        cursor: pointer;
        transition: background-color 350 ease-in-out;
    }
</style>