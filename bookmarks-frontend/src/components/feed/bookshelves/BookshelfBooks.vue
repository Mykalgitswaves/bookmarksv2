<template>
    <ul class="bookshelf-books" ref="books" v-if="books.length">
        <li class="bs-b-wrapper">
            <button
                v-if="(currentBook && currentBook.id !== books[0].id) && !isEditing"
                class="swap-btn-target"
                type="button"
                @click="swapToBeginningOfList()"
                >Start</button>
        </li>

        <li v-for="(book, index) in books" :key="index" class="bs-b-wrapper">
            <SortableBook
                :order="index"
                :id="book?.id"
                :bookTitle="book?.title"
                :author="book?.author_names || book?.authors"
                :imgUrl="book?.small_img_url"
                :next-book="books[index + 1]"
                :prev-book="books[index - 1]"
                :current-book="currentBook"
                :current-book-for-overlay="currentBookForOverlay"
                :index="index"
                :is-editing="isEditing"
                :note-for-shelf="book.note_for_shelf"
                :unique="unique"
                @set-sort="(data) => setSort(data)"
                @swapped-with="(data) => swappedWithHandler(data)"
                @removed-book="$emit('removed-book', $event)"
                @show-book-controls-overlay="(bookPayload) => showBookControlsOverlayHandler(bookPayload)"
            />
        </li>

        <!-- For swapping to end of the list. -->
        <li class="bs-b-wrapper">
            <button
                v-if="(currentBook && currentBook.id !== books[books.length - 1].id) && !isEditing"
                class="swap-btn-target"
                type="button"
                @click="swapToEndOfList()"
            >End</button>
        </li>
    </ul>


    <!-- This is for flow shelves -->
    <teleport v-if="showBookControlsOverlay" to="body">
        <div class="book-controls-overlay shadow-lg" v-if="currentBookForOverlay">
            <div class="flex">
                <span class="hidden">Book controls</span>

                <button    
                    class="ml-auto" 
                    type="button"
                    role="close-modal"
                    @click="currentBookForOverlay = null; showBookControlsOverlay = false;"
                >
                    <IconExit />
                </button>
            </div>

            <p class=" mb-5 text-center text-xl fancy text-indigo-500">
                {{ currentBookForOverlay.title }}
            </p>
            <!-- Move to shelves select -->
            <div v-if="userShelves">
                <label class="select-1" for="moveToShelf">
                    <span class="text-stone-600">Move to shelf</span>
                
                    <select class="block w-100 mt-2" name="" id="moveToShelf" v-model="moveToSelectedShelfData.shelf">
                        <option v-for="shelf in userShelves" :key="shelf.id" :value="shelf.id">
                            {{ shelf.title }}
                        </option>
                    </select>
                </label>
            </div>

            <div v-if="moveToSelectedShelfData.shelf === Bookshelves.CURRENTLY_READING.prefix">
                <div class="mt-5">
                    <label class="text-stone-600" for="currentlyReading">
                        <b>Optional: </b>
                        Why are you starting this book?
                    </label>

                    <textarea class="w-100 mt-2 border-2 border-indigo-200 br-input-normal input-base-padding" 
                        name="currently_reading_textarea"
                        id="currentlyReading"
                        v-model="moveToSelectedShelfData.note" 
                    />
                </div>

                <div class="mt-5 flex space-between">
                    <button class="btn btn-submit small" type="button">
                        Move to shelf
                    </button>
                    
                    <button class="btn btn-red btn-remove icon small" type="button">
                        <IconTrash />
                        <span class="hidden-on-mobile">Remove from current shelf</span>
                    </button>
                </div>
            </div>
        </div>
    </teleport>
    <!-- endFlowShelves -->

    <!-- Regular shelves -->
    <teleport v-if="currentBook !== null || canReorder || isEditing" to="body">
        <div class="sorting-footer">
            <div v-if="currentBook" class="s-f-book">
                <img :src="currentBook.small_img_url" class="s-f--current-book-img" alt="">

                <h3 class="s-f--current-book">
                {{ selectedBookToBeMoved }}
                </h3>
            </div>

            <h3 v-else>
                <span v-if="canReorder">Click on a book to reorder</span> 

                <span v-if="isEditing">Click on a book to edit</span> 
            </h3>

            <div class="sorting-footer-controls">
                <button type="button" class="btn s-f-c--btn" @click="resetSort()">
                    Cancel
                </button>
            </div>
        </div>    
    </teleport>
    <!-- End regular shelves -->
</template>
<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import SortableBook from './SortableBook.vue';
import IconExit from '../../svg/icon-exit.vue';
import IconTrash from '../../svg/icon-trash.vue';
import { db } from '../../../services/db';
import { urls } from '../../../services/urls';
import { Bookshelves } from '../../../models/bookshelves';

const props = defineProps({
    books: {
        type: Array,
        required: false,
        default: [],
    },
    isReordering: {
        type: Boolean,
    },
    canReorder: {
        type: Boolean,
        default: false,
    },
    isEditing: {
        type: Boolean,
        default: false,
    },
    unsetCurrentBook: {
        type: Number,
        required: true,
    },
    unique: {
        type: String,
        required: false,
        default: '',
    }
});

const route = useRoute();
const { user } = route.params;
const emit = defineEmits(['send-bookdata-socket', 'cancelled-reorder']);
const userShelves = ref([]);
const loaded = ref(false);
const FLOWSHELVES = [Bookshelves.WANT_TO_READ, Bookshelves.CURRENTLY_READING, Bookshelves.FINISHED_READING];


FLOWSHELVES.filter((shelf) => (shelf.prefix !== props.unique)).forEach(
        (shelf) => {
        // We need to get the users visbiility for each shelf.
        let _shelf = Bookshelves.formatFlowShelf(shelf, 'private');
        userShelves.value.push(_shelf);
    }
);


onMounted(async () => {
    await db.get(
        urls.rtc.minimalBookshelvesForLoggedInUser(user)
    ).then((res) => {
        userShelves.value.push(...res.bookshelves);
        loaded.value = true;
    });
});


const moveToSelectedShelfData = ref({
    note: '', 
    shelf: '',
});

// used for moving books to diff shelves in flow shelves.
function setCurrentBookForOverlayOnMoveToSelectedShelfData(bookData) {
    console.log('setting move to selected shelf data for book');
    moveToSelectedShelfData.value.book = bookData;
};


// This is what will be sent via websocket over the wire.
let bookdata = {
    target_id: null,
    previous_book_id: null,
    next_book_id: null,
    author_id: user,
};

const currentBook = ref(null);
watch(() => props.unsetCurrentBook, (newVal) => {
    if(newVal){
        currentBook.value = null;
    }
});


const selectedBookToBeMoved = computed(() => 
    `#${currentBook.value?.order ?? ''} ${currentBook.value?.title}`
);


// Used to set the current target
function setCurrentBook(bookData) {
    currentBook.value = props.books.find((b)=> b.id === bookData);
}


// early step of swap, sets currentBook.
function setSort(bookData) {
    if(props.canReorder || props.isEditing){
        console.assert(bookData !== (null || undefined));
        bookdata.target_id = bookData;
        setCurrentBook(bookData);
    }
};


// When someone cancels.
function resetSort() {
    currentBook.value = null;
    //  Reset all properties of this object.
    bookdata = {
        target_id: null,
        previous_book_id: null,
        next_book_id: null,
        author_id: user
    };
    if(props.canReorder){
        emit('cancelled-reorder')
    } else if (props.isEditing){
        emit('cancelled-edit')
    }
};


// Specific function for swapping to end of list.
function swapToEndOfList() {
    bookdata = {
        target_id: currentBook.value.id,
        previous_book_id: props.books[props.books.length - 1].id,
        next_book_id: null,
        author_id: user
    }

    emit('send-bookdata-socket', bookdata);
}


function swapToBeginningOfList() {
    bookdata = {
        target_id: currentBook.value.id,
        previous_book_id: null,
        next_book_id: props.books[0].id,
        author_id: user
    }

    emit('send-bookdata-socket', bookdata);
}


// Setting up data needed for EditBookshelf's reorder function.
function swappedWithHandler(book_data) {
    let prev = props.books[book_data.target_index]

    let next = props.books[book_data.target_index + 1]

    bookdata.previous_book_id = prev ? prev.id : null;
    bookdata.next_book_id = next ? next.id : null;

    emit('send-bookdata-socket', bookdata);
};


/**
 * Book controls overlay functions.
 */
const currentBookForOverlay = ref(null);
const showBookControlsOverlay = ref(false);
// ------------------------------
function showBookControlsOverlayHandler(payload){
    showBookControlsOverlay.value = true;
    let res = Object.values(payload)
    let id = res[0];
    if(!id) console.warn('No id found in payload');
    currentBookForOverlay.value =  props.books.find((_book) => _book.id === id);
    setCurrentBookForOverlayOnMoveToSelectedShelfData(currentBookForOverlay.value);
}
</script>
<style scoped lang="scss">
    .book-controls-overlay {
        --inline-offset: -49%;
        @media screen and (max-width: 768px) {
            --inline-offset: -50%;
        }
        padding-top: 18px;
        padding-bottom: 18px;
        padding-left: 14px;
        padding-right: 14px;;
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(var(--inline-offset), -50%);
        width: clamp(300px, 100%, 500px);
        min-height: 280px;
        background-color: var(--semi-transparent-surface);
        border-radius: var(--radius-sm);
        border: 1px solid var(--stone-200);
    }

    .bookshelf-books {
        display: grid;
        // padding-top: var(--padding-sm);/
        row-gap: 8px;
    }

    .s-f-c--btn {
        border-radius: var(--radius-sm);
        background-color: var(--red-100);
        color: var(--red-700);
        padding-left: 12px;
        padding-right: 12px;
    }

    .s-f-c--btn:hover {
        background-color: var(--red-200);
        transition: 250ms ease;
    }


    .s-f-book {
        display: flex;
        column-gap: 14px;
        align-items: center;
    }

    .s-f--current-book {
        font-size: var(--font-xl);
        font-weight: 500;
    }

    .s-f--current-book-img {
        width: 40px;
        border-radius: var(--radius-sm);
    }

    .bs-b-wrapper {
        display: flex;
        flex-direction: column;
        row-gap: 12px;
        margin-top: 10px;
        margin-bottom: 10px;
        align-items: center;
        width: 100%;
    }
</style>