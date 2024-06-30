<template>
    <h1 class="work-feed-heading">Currently Reading
        <br><span class="text-sm">Update books you are reading</span>

    </h1>
        <!-- If loaded -->
        <div class="currently-reading" v-if="currentlyReadingBooks?.length">
            <div class="currently-reading-book" 
                v-for="book in currentlyReadingBooks" 
                :key="book.id"   
                role="button" 
                @click="showCurrentlyReadingBookOverlay(book)"
            >
                <img class="book-img" :src="book.small_img_url"/>

                <h4 class="book-title text-stone-500">{{ truncateText(book.title, 64) }}</h4>
                
                <div class="book-metadata">
                    <p class="progress">70 / 140</p>
                </div>
            </div>
        </div>

        <!-- IF loading -->
        <div class="currently-reading" v-else>
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
<script setup>
import { db } from '../../services/db';
import { urls } from '../../services/urls';
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { truncateText } from '../../services/helpers';

const route = useRoute();
const { user } = route.params;
const data = ref(null);

onMounted(async() => {
    db.get(urls.rtc.getCurrentlyReadingPreview(user)).then((res) => {
        data.value = res.bookshelf;
    });
});

const currentlyReadingBooks = computed(() => {
    if (!data.value) return [];
    let books = []; 
    for(let i = 0; i < data.value.books_count; i++) {
        let book = {
            small_img_url: data.value.book_img_urls[i],
            book_id: data.value.book_ids[i],
            title: data.value.book_titles[i],
        }
        books.push(book);
    }
    return books;
})

// function showCurrentlyReadingBookOverlay(book){
//     currentlyReadingControls.value
// }

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