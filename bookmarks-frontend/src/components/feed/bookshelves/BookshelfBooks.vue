<template>
    <ul class="bookshelf-books" ref="books" v-if="books.length">
        <li class="bs-b-wrapper">
            <button
                v-if="currentBook && (currentBook?.id !== books[0].id) && isEditing"
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
                :book="book"
                :current-book="currentBook"
                :current-book-for-overlay="currentBookForOverlay"
                :index="index"
                :is-editing="isEditing"
                :note-for-shelf="book.note_for_shelf"
                :unique="unique"
                @editing-current-book-note="(book) => startEditingCurrentBookNote(book)"
                @set-sort="(data) => setSort(data)"
                @swapped-with="(data) => swappedWithHandler(data)"
                @removed-book="$emit('removed-book', $event)"
                @show-book-controls-overlay="(bookPayload) => showBookControlsOverlayHandler(bookPayload)"
                @update-currently-reading-book="(bookPayload) => showCreateUpdateOverlayHandler(bookPayload)"
            />
        </li>

        <!-- For swapping to end of the list. -->
        <li class="bs-b-wrapper">
            <button
                v-if="(currentBook && currentBook.id !== books[books.length - 1].id) && isEditing"
                class="swap-btn-target"
                type="button"
                @click="swapToEndOfList()"
            >End</button>
        </li>
    </ul>

    <!-- ------------------------------------------------- -->
    <!-- this is for creating updates on currently reading shelves-->
    <teleport 
        v-if="unique === Bookshelves.CURRENTLY_READING.prefix && isUpdatingCurrentlyReadingBook && currentBook" 
        to="body"
    >

        <div class="book-controls-overlay shadow-lg">
            <button type="button" class="btn btn-small icon" @click="resetSort()">
                <IconExit />
            </button>

            <CreateUpdateForm :book="currentBook" @post-update="$emit('post-update', $event)">
                
            </CreateUpdateForm>
        </div>
    </teleport>

    <!-- ------------------------------------------------- -->
    <!-- This is for flow shelves -->
    <teleport v-if="showBookControlsOverlay" to="body">
        <div class="book-controls-overlay shadow-lg" 
            v-if="currentBookForOverlay"
        >
            <div class="flex">
                <span class="hidden">Book controls</span>

                <button    
                    class="btn btn-ghost pl-0 pr-0 pt-0 pb-0 ml-auto" 
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
                    <span class="text-stone-600 bold">Move to shelf</span>
                
                    <select class="block w-100 mt-2" name="" id="moveToShelf" v-model="moveToSelectedShelfData.shelf">
                        <option v-for="shelf in userShelves" :key="shelf.id" :value="shelf.id">
                            {{ shelf.title }}
                        </option>
                    </select>
                </label>
            </div>
            
            <!-- <div class="w-100" :class="{'mt-5': !editingCurrentBookNote}">
                <button 
                    type="button"
                    class="text-stone-500 underline pl-2"
                    @click="setOrUnsetEditingCurrentBookNote"
                >
                    <span v-if="!editingCurrentBookNote">Edit note for this book</span>
                </button>
            </div>

            <div v-if="editingCurrentBookNote">
                <textarea class="add-book-note" 
                    id="current-book-note-for-shelf-textarea"
                    :ref="(el) => (textAreas.wantToReadNoteTextArea = el)"
                    name="note_for_shelf"
                    :style="{ 'height':  heights.note_for_shelf + 'px' }"
                    v-model="currentBookForOverlay.note_for_shelf"
                    @input="generatedHeightForTextArea(textAreas.wantToReadNoteTextArea)"
                ></textarea>
                Saving the note you just made -->
                <!-- <div class="flex justify-between mt-5">
                    <button type="button" class="btn btn-submit" @click="saveBookNoteForCurrentBook()">
                        Save
                    </button>
                    <button type="button" class="btn btn-red" @click="setOrUnsetEditingCurrentBookNote">
                        cancel
                    </button>
                </div>
            </div> -->

            <!-- Move to currently reading code and not editing current book note for shelf -->
            <div v-if="moveToSelectedShelfData.shelf === Bookshelves.CURRENTLY_READING.prefix && !editingCurrentBookNote">
                <div class="mt-5">
                    <label class="text-stone-600" for="currentlyReading">
                        <b>Optional: </b>
                        Why are you starting this book?
                    </label>
                    
                    <textarea class="w-100 mt-2 border-2 border-indigo-200 br-input-normal input-base-padding min-height-textarea " 
                        :ref="(el) => (textAreas.currentlyReadingTextArea = el)"
                        :style="{ 'height':  heights[Bookshelves.CURRENTLY_READING.prefix] + 'px' }"
                        :name="Bookshelves.CURRENTLY_READING.prefix"
                        id="currentlyReading"
                        v-model="moveToSelectedShelfData.note" 
                        @input="generatedHeightForTextArea(textAreas.currentlyReadingTextArea)"
                    />
                </div>

                <div class="mt-5  place-content-center">
                    <button class="btn btn-submit small" type="button" @click="moveToShelf(moveToSelectedShelfData.shelf)">
                        Move to shelf
                    </button>
                    
                    <label class="flex items-center gap-2 mt-5" for="removeFromCurrentShelf">
                        <input type="checkbox" v-model="moveToSelectedShelfData.isRemovingFromCurrentShelf">
                        <span class="text-sm text-stone-500">Remove this book from the current shelf</span>
                    </label>
                </div>
            </div>

            <!-- Moving something to finished reading shelf -->
            <div v-if="moveToSelectedShelfData.shelf === Bookshelves.FINISHED_READING.prefix">
                <div class="mt-5 place-content-center" 
                    v-if="!isMakingReviewFromCurrentlyReading"
                >
                    <label class="flex items-center gap-2 mb-5 ml-auto mr-auto" for="removeFromCurrentShelf">
                        <input type="checkbox" v-model="moveToSelectedShelfData.isRemovingFromCurrentShelf">
                        <span class="text-sm text-stone-500">Remove this book from the current shelf</span>
                    </label>

                    <button 
                        type="button" 
                        class="btn btn-submit small"
                        @click="isMakingReviewFromCurrentlyReading = true"
                    >
                        I finished reading this book
                    </button>
                </div>

                <!-- Force users to create reviews from post data -->
                <div>
                    <CreateReviewPost
                        v-if="isMakingReviewFromCurrentlyReading"
                        :book="currentBookForOverlay"
                        :is-postable-data="postableReviewData"
                        :unique="Bookshelves.CURRENTLY_READING.prefix"
                        @is-postable-data="(updatedPostableData) => 
                            updatePostableDataHandler(updatedPostableData)"
                        @post-data="postReviewAndMoveBookToShelf()"
                    />
                </div>
            </div>
            
            <div v-if="moveToSelectedShelfData.shelf === Bookshelves.WANT_TO_READ.prefix"
                class="mt-5 place-content-center"
            >
                <button type="button" 
                    class="btn btn-submit small" 
                    @click="moveToShelf(moveToSelectedShelfData.shelf)"
                >
                    Move to shelf
                </button>
            </div>

            <!-- for everything else -->
            <div v-if="!isFlowShelf">
                <div class="mt-5 place-content-center">
                    <button 
                        type="button" 
                        class="btn btn-submit small" 
                        @click="moveToShelf(moveToSelectedShelfData.shelf)"
                    >
                        Move to shelf
                    </button>
                    <label class="flex items-center gap-2 mt-5" for="removeFromCurrentShelf">
                        <input type="checkbox" v-model="moveToSelectedShelfData.isRemovingFromCurrentShelf">
                        <span class="text-sm text-stone-500">Remove this book from the current shelf</span>
                    </label>
                </div>
            </div>
        </div>
    </teleport>
    <!-- endFlowShelves -->
    <!-- ------------------------------------------------- -->

    <!-- Regular shelves -->
    <teleport v-if="(currentBook !== null || canReorder || isEditing) && !isUpdatingCurrentlyReadingBook " to="body">
        <div class="sorting-footer">
            <div v-if="currentBook" class="s-f-book">
                <img :src="currentBook.small_img_url" class="s-f--current-book-img" alt="">

                <h3 class="s-f--current-book">
                {{ selectedBookToBeMoved }}
                </h3>
            </div>

            <h3 v-else>
                <span class="fancy text-stone-700">Click on a book to edit</span> 
            </h3>

            <div class="flex gap-2 items-center">
                <button v-if="currentBook" 
                    type="button"
                    class="btn btn-tiny text-sm text-stone-400 icon mr-5" 
                    @click="startEditingCurrentBookNote(currentBook)"
                >
                    <IconNote />
                </button>

                <button 
                    v-if="currentBook" 
                    type="button" 
                    class="btn btn-tiny text-sm text-red-500 btn-remove icon mr-5" 
                    @click="emit('removed-book', currentBook.id)"
                >
                    <IconTrash />
                    Remove from shelf
                </button>

                <button type="button" class="btn s-f-c--btn" @click="resetSort()">
                    Cancel
                </button>
            </div>
        </div>    
    </teleport>
    <!-- End regular shelves -->

    <!-- Edit a books note -->
    <Overlay 
        :ref="(el) => editNoteOverlay = el?.dialogRef" 
        @closed-modal="currentBook = null"
    >
        <template #overlay-main>
            <div style="min-width: 300px; width: 60vw; max-width: 600px;"> 
                <GenericTextArea 
                    name="current-book-note" 
                    :v-model="currentBook?.note_for_shelf"
                    @updated:modelValue="(noteForShelf) => currentBook.note_for_shelf = noteForShelf"    
                >
                    <template #labelAbove>
                        Note for shelf
                    </template>
                </GenericTextArea>
            </div>
        </template>
        <template #overlay-footer>
            <button
                type="button" 
                :disabled="!currentBook?.note_for_shelf"
                class="mt-5 btn btn-submit btn-wide" 
                @click="submitNoteForShelfForCurrentBook(currentBook)">
                Submit
            </button>
        </template>
    </Overlay>
    
    <Transition name="content">
        <ErrorToast v-if="error.isShowing" :message="error.message" :refresh="true"/>
    </Transition>
    <Transition name="content">
        <SuccessToast v-if="toast" :message="toast.message" /> 
    </Transition>
</template>
<script setup>
import { ref, computed, watch, onMounted, toRaw, defineExpose } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import SortableBook from './SortableBook.vue';
import IconExit from '../../svg/icon-exit.vue';
import IconTrash from '../../svg/icon-trash.vue';
import { db } from '../../../services/db';
import { urls, navRoutes } from '../../../services/urls';
import { Bookshelves } from '../../../models/bookshelves';
import { helpersCtrl, createConfetti } from '../../../services/helpers';
import CreateUpdateForm from '../createPosts/update/createUpdateForm.vue';
import CreateReviewPost from '../createPosts/createReviewPost.vue'
import ErrorToast from '../../shared/ErrorToast.vue';
import SuccessToast from '../../shared/SuccessToast.vue';
import Overlay from '../partials/overlay/Overlay.vue';
import GenericTextArea from '../partials/GenericTextArea.vue';

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
const router = useRouter();
const { user, bookshelf } = route.params;
const emit = defineEmits(['send-bookdata-socket', 'cancelled-reorder', 'start-ws-connection']);
const userShelves = ref([]);
const loaded = ref(false);
const FLOWSHELVES = [Bookshelves.WANT_TO_READ, Bookshelves.CURRENTLY_READING, Bookshelves.FINISHED_READING];
const error = ref({
    isShowing: false,
    message: '',
});
const toast = ref(null);
const editNoteOverlay = ref(null)

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
    isRemovingFromCurrentShelf: false,
});


//  Two defaults for whether a shelf is WANT TO READ or CURRENTLY READING.
if (props.unique === Bookshelves.WANT_TO_READ.prefix) {
    moveToSelectedShelfData.value.shelf = Bookshelves.CURRENTLY_READING.prefix;
}

if (props.unique === Bookshelves.CURRENTLY_READING.prefix) {
    moveToSelectedShelfData.value.shelf = Bookshelves.FINISHED_READING.prefix;
}


// Used for moving books to diff shelves in flow shelves.
function setCurrentBookForOverlayOnMoveToSelectedShelfData(bookData) {
    console.log('setting move to selected shelf data for book');
    moveToSelectedShelfData.value.book = bookData;
};


// Default refs for the textareas we are adjusting.
const textAreas = ref({
    currentlyReadingTextArea: null,
    wantToReadNoteTextArea: null,
});


// ------------------------------
// For getting height of the textarea.
const { debounce } = helpersCtrl;
const heights = ref({});


// Defaults for heights
heights.value[Bookshelves.CURRENTLY_READING.prefix] = 82;
heights.value.note_for_shelf = 82;
heights.value[Bookshelves.FINISHED_READING.prefix] = 82;
heights.value[Bookshelves.WANT_TO_READ.prefix] = 82;


function generatedHeightForTextArea(refEl) {
    // Temporarily set height to 'auto' to reset and measure content height
    refEl.style.height = 'auto';

    // Calculate the new height based on scrollHeight
    const newHeight = `${Math.max(refEl.scrollHeight, 82)}px`; // Enforce minimum height of 82px

    // Update the height only if it's different from the current height
    if (refEl.style.height !== newHeight) {
        refEl.style.height = newHeight; // Apply the new height

        // Update the stored height if applicable (optional for tracking)
        if (refEl.name === Bookshelves.CURRENTLY_READING.prefix) {
            heights.value[Bookshelves.CURRENTLY_READING.prefix] = refEl.scrollHeight;
        }

        if (refEl.name === Bookshelves.FINISHED_READING.prefix) {
            heights.value[Bookshelves.FINISHED_READING.prefix] = refEl.scrollHeight;
        }

        if (refEl.name === Bookshelves.WANT_TO_READ.prefix) {
            heights.value[Bookshelves.WANT_TO_READ.prefix] = refEl.scrollHeight;
        }

        if (refEl.name === 'note_for_shelf') {
            heights.value[Bookshelves.WANT_TO_READ.note_for_shelf] = refEl.scrollHeight;
        }
    }
}

// This sucked so I dont use it. Typing experience has janky
const debouncedScrollHeightForTextArea = debounce(generatedHeightForTextArea, 150, true)

// End height functions
// ------------------------------

// ------------------------------------------------------
// Functions that have to do with server stuff and setting 
// / unsetting current books
// ------------------------------------------------------


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
        console.log('here dude', bookData)
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
    
    emit('cancelled-edit')
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
 * Book controls overlay functions for generic shelves.
 */
const currentBookForOverlay = ref(null);
// note this is not the same overlay being used when you create a progress update
const showBookControlsOverlay = ref(false);
const editingCurrentBookNote = ref(false);
// ------------------------------


function showBookControlsOverlayHandler(payload){
    if (!props.isEditing) {
        showBookControlsOverlay.value = true;
        let res = Object.values(payload)
        let id = res[0];
        if(!id) console.warn('No id found in payload');
        currentBookForOverlay.value =  props.books.find((_book) => _book.id === id);
        setCurrentBookForOverlayOnMoveToSelectedShelfData(currentBookForOverlay.value);
    }
}


function setOrUnsetEditingCurrentBookNote() {
    if(editingCurrentBookNote.value){
        editingCurrentBookNote.value = false;
        heights.value.note_for_shelf = 82;
    } else {
        editingCurrentBookNote.value = true;
    }
}


async function saveBookNoteForCurrentBook(isDebug) {
    let _data = {
        book_id: currentBookForOverlay.value.id,
        note_for_shelf: currentBookForOverlay.value.note_for_shelf,
    };

    if (isDebug) {
        console.log(_data);
    }

    await db.put(urls.rtc.updateBookNoteForShelf(route.params.bookshelf), _data).then((res) => {
        console.log(res);
    });
}


/**
 * @async
 * @description: Wrapper around the Bookshelves.moveBookToShelf function.
 * @param {*} bookshelf - bookshelf id of the shelf you want to move things to.
 */
function moveToShelf(bookshelf) {
    const authors = toRaw(currentBookForOverlay.value.author_names) || toRaw(currentBookForOverlay.value.authors)
    const book = {
        title: currentBookForOverlay.value.title,
        author_names: authors,
        small_img_url: currentBookForOverlay.value.small_img_url,
        id: currentBookForOverlay.value.id,
        noteForShelf: currentBookForOverlay.value.note_for_shelf,
    }

    try {
        let currentShelf = moveToSelectedShelfData.value.isRemovingFromCurrentShelf ? route.params.shelf : '';
        Bookshelves.moveBookToShelf(bookshelf, book, currentShelf);
    } catch (error) {
        error.value.message = `Error moving book, it may already be in this shelf.`
        error.value.isShowing = true;
        setTimeout(() => {
            error.value.isShowing = false;
        }, 5000);
        console.error(error);
    };
    if (!isUpdatingCurrentlyReadingBook || !(bookshelf === Bookshelves.FINISHED_READING.prefix)) {
        console.log('closing overlay');
        showBookControlsOverlay.value = false;
        toast.value = {
            message: `Book moved to shelf`,
        };
        setTimeout(() => {
            toast.value = null;
        }, 5000);
    }
    
}

// Edit note functions
// ------------------------------



function startEditingCurrentBookNote(book) {
    emit('start-ws-connection')
    currentBook.value = book;
    editNoteOverlay.value?.showModal();
}

async function submitNoteForShelfForCurrentBook(book) {
    db.put(urls.rtc.updateBookNoteForShelf(bookshelf), {
        book_id: book.id,
        note_for_shelf: book.note_for_shelf,
        id: bookshelf,
    }, false, (res) => {
        editNoteOverlay.value?.close();
    }, (err) => {
        console.error(err);
    });
};

// ------------------------------
//

// End of book controls overlay function
// ------------------------------


// For reggie shelves not flowshelves.
const isFlowShelf = computed(() => {
    return !![
        Bookshelves.FINISHED_READING.prefix, 
        Bookshelves.CURRENTLY_READING.prefix,
        Bookshelves.WANT_TO_READ.prefix
    ].includes(moveToSelectedShelfData.value.shelf);
});


/**
 * Currently reading book update functionality
 * -------------------------------------------
 */

const isUpdatingCurrentlyReadingBook = ref(false);

function showCreateUpdateOverlayHandler(book) {
    isUpdatingCurrentlyReadingBook.value = true;
    currentBook.value = book;
}


/**
 * @finished_reading_shelf_functions
 * Functions for moving books in currently reading to finished reading shelf 
 * 
 * --------------------------------------------------------------------------------------
 * @function updatePostableDataHander
 * @description Does the fancy logic needed to let us know whether or not we can move from one shelf to another.
 * @dependency – postableReviewData -  a ref that is mutated by the function
 * @param {Object} updatedpostableData - payload from createReviewPost component emit
 * @returns { Void|null } nothing
 * --------------------------------------------------------------------------------------
 */
 
 // dependency for the ui, needs to be a ref.
 const isMakingReviewFromCurrentlyReading = ref(false);
 // dependency for function
 const postableReviewData = ref({});

 function updatePostableDataHandler(updatedpostableData) {
    postableReviewData.value = updatedpostableData;
 };

 /**
 * --------------------------------------------------------------------------------------
 * @function postReviewandMoveBookToShelf
 * @description 
 */

 function postReviewAndMoveBookToShelf() {
    const postBookPromise = db.post(
        urls.reviews.review, 
        postableReviewData.value, 
        true, 
    (res) => {
        console.log(res, 'succeeded')
    },
    (err) => {
        console.log(err, 'something weird happend');
    });

    const moveBookToShelfPromise = db.put(
        urls.rtc.quickAddBook(Bookshelves.FINISHED_READING.prefix), 
        {
            book: {
                title: currentBookForOverlay.value.title,
                author_names: currentBookForOverlay.value.authors,
                small_img_url: currentBookForOverlay.value.small_img_url,
                id: currentBookForOverlay.value.id,
            },
            note: '',
        }, 
        true,
    );

    // Confetti, then reroute to the posted book review.
    Promise.all([postBookPromise, moveBookToShelfPromise]).then(() => {
        createConfetti();
        setTimeout(() => {
            router.push(navRoutes.toLoggedInFeed(route.params.user));
        }, 1);
    }).catch((err) => console.log(err));
 };

 /**
  * end of functions
  * -------------------------------------------------------------------------------------
  * -------------------------------------------------------------------------------------
  */

  
// Expose macros for flow shelf capabilities
defineExpose({ currentBook });

/**
 * Fin currently reading book update functionality
 */
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
        width: clamp(300px, 90%, 800px);
        min-height: 280px;
        background-color: var(--semi-transparent-surface);
        border-radius: var(--radius-sm);
        border: 1px solid var(--stone-200);
        max-height: 87vh;
        overflow-y: scroll;
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