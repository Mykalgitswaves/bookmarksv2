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
                        <AsyncComponent :promises="[getBookshelvesMinimalPreviewPromise]">
                            <template #resolved>
                                <div v-if="bookshelves">
                                    <label class="select-1" for="moveToShelf">
                                        <span class="text-stone-600 bold">Move to shelf</span>
                                    
                                        <select class="block w-100 mt-2" name="" id="moveToShelf" v-model="moveToSelectedShelfData.shelf">
                                            <option v-for="shelf in bookshelves" :key="shelf.id" :value="shelf.id">
                                                {{ shelf.title }}
                                            </option>
                                        </select>
                                    </label>
                                </div>
                                <div class="mt-5">
                                    <label class="text-stone-600">
                                        <b>Optional: </b>
                                        Add a note for this book
                                    </label>
                                    <!-- NOTE: This originally had an @input in it, but I didn't understand it so I removed it. -->
                                     <!-- Something to do with debounce, maybe we can add it back together -->
                                    <textarea class="w-100 mt-2 border-2 border-indigo-200 br-input-normal input-base-padding min-height-textarea" 
                                        :style="{ 'height':  heights[note_for_shelf] + 'px' }"
                                        :ref="(el) => (textAreas.noteTextArea = el)"
                                        name="note_for_shelf"
                                        v-model="moveToSelectedShelfData.note" 
                                        @input="generatedHeightForTextArea(textAreas.noteTextArea)"
                                    />
                                </div>
                                <div class="mt-5 place-content-center">
                                    <button type="button" 
                                        class="btn btn-submit small" 
                                        @click="moveToShelf(moveToSelectedShelfData.shelf, overlayRef)"
                                    >
                                        Move to shelf
                                    </button>
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
    <Transition name="content">
        <ErrorToast v-if="error.isShowing" :message="error.message" :refresh="true"/>
    </Transition>
    <Transition name="content">
        <SuccessToast v-if="toast" :message="toast.message" /> 
    </Transition>
</template>

<script setup>
// import SimilarBooks from '@/components/feed/SimilarBooks.vue';
import { ref, computed, toRaw } from 'vue';
import { useRoute, useRouter } from 'vue-router'
import { db } from '../../services/db';
import { urls } from '../../services/urls';
import { helpersCtrl } from '../../services/helpers';
import IconPlus from '../svg/icon-plus.vue';
import LoadingCard from '../shared/LoadingCard.vue'
import IconAddReview from '../svg/icon-add-post.vue';
import Overlay from './partials/overlay/Overlay.vue';
import { hideOverlay, showOverlay } from './partials/overlay/overlay-service.js';
import AsyncComponent from './partials/AsyncComponent.vue';
import { Bookshelves } from '../../models/bookshelves';
import ErrorToast from '../shared/ErrorToast.vue';
import SuccessToast from '../shared/SuccessToast.vue';

const route = useRoute();
const router = useRouter();
const { commanator } = helpersCtrl;
const { user, work } = route.params;
const book_id = route.params.version ? route.params.version : route.params.work;
const overlayRef = ref(null);
const book = ref(null);
const filterPopout = ref(false);
const FLOWSHELVES = [Bookshelves.WANT_TO_READ, Bookshelves.CURRENTLY_READING, Bookshelves.FINISHED_READING];
const _flowshelves = [...FLOWSHELVES];
const error = ref({
    isShowing: false,
    message: '',
});
const toast = ref(null);

let bookshelves = [];

_flowshelves.forEach(
        (shelf) => {
        // We need to get the users visbiility for each shelf.
        let _shelf = Bookshelves.formatFlowShelf(shelf, 'private');
        bookshelves.push(_shelf);
    }
);

async function getWorkPage() {
    await db.get(urls.books.getBookPage(book_id), null, true).then((res) => {
        book.value = res.data;
    })
}

getWorkPage()

const book_img = computed(() => (book.value?.small_img_url || book.value?.img_url));
const postOptions = ["review", "update", "comparison"];

const mapping = {
  "review": `/feed/${user}/create/review/${work}`,
  "update": `/feed/${user}/create/update/${work}`,
  "comparison": `/feed/${user}/create/comparison/${work}`,
};

const moveToSelectedShelfData = ref({
    note: '', 
    shelf: Bookshelves.WANT_TO_READ.prefix,
    isRemovingFromCurrentShelf: false,
});

// Default refs for the textareas we are adjusting.
const textAreas = ref({
    noteTextArea: null
});

const { debounce } = helpersCtrl;
const heights = ref({});

// Defaults for heights
heights.value.note_for_shelf = 82;

function generatedHeightForTextArea(refEl) {
    // Temporarily set height to 'auto' to reset and measure content height
    refEl.style.height = 'auto';

    // Calculate the new height based on scrollHeight
    const newHeight = `${Math.max(refEl.scrollHeight, 82)}px`; // Enforce minimum height of 82px

    // Update the height only if it's different from the current height
    if (refEl.style.height !== newHeight) {
        refEl.style.height = newHeight; // Apply the new height

        if (refEl.name === 'note_for_shelf') {
            heights.value[Bookshelves.WANT_TO_READ.note_for_shelf] = refEl.scrollHeight;
        }
    }
}

const getBookshelvesMinimalPreviewPromise = db.get(urls.rtc.minimalBookshelvesForLoggedInUser(user), null, false, 
    (res) => {
        bookshelves.push(...res.bookshelves);
    }, (err) => {
        console.log(err);
    }
);

function testOnClick() {
    console.log(moveToSelectedShelfData.value.note)
};

async function moveToShelf(bookshelf, overlayRef) {
    const authors = toRaw(book.value.author_names) || toRaw(book.value.authors)
    const book_to_add = {
        title: book.value.title,
        author_names: authors,
        small_img_url: book.value.small_img_url,
        id: book.value.id || book.value.google_id,
        noteForShelf: moveToSelectedShelfData.value.note,
    }
    let currentShelf = '';
   
    try {
        console.log(book_to_add)
        const response = await Bookshelves.moveBookToShelf(bookshelf, book_to_add, currentShelf);
        hideOverlay(overlayRef);
        toast.value = { message: "Book moved to shelf" };
        setTimeout(() => {
            toast.value = null;
        }, 5000);
        console.log(response);
    } catch (error) {
        hideOverlay(overlayRef);
        error.value.message = 'Error moving book, it may already be in this shelf.'
        error.value.isShowing = true;
        setTimeout(() => {
            error.isShowing = false;
        }, 5000);
        console.error(error);
    }
}

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