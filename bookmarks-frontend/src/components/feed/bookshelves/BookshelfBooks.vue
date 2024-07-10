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
                <template #set-current-page>
                    <button type="button" @click="setCurrentPageOnly">update page and skip review</button>
                </template>
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
            
            <div class="w-100" :class="{'mt-5': !editingCurrentBookNote}">
                <button 
                    v-if="moveToSelectedShelfData.shelf === Bookshelves.CURRENTLY_READING.prefix"
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
                    @input="throttledScrollHeightForTextArea(textAreas.wantToReadNoteTextArea)"
                ></textarea>
                <!-- Saving the note you just made -->
                <div class="flex justify-between mt-5">
                    <button type="button" class="btn btn-submit" @click="saveBookNoteForCurrentBook()">
                        Save
                    </button>
                    <button type="button" class="btn btn-red" @click="setOrUnsetEditingCurrentBookNote">
                        cancel
                    </button>
                </div>
            </div>

            <!-- Move to currently reading code and not editing current book note for shelf -->
            <div v-if="moveToSelectedShelfData.shelf === Bookshelves.CURRENTLY_READING.prefix && !editingCurrentBookNote">
                <div class="mt-5">
                    <label class="text-stone-600" for="currentlyReading">
                        <b>Optional: </b>
                        Why are you starting this book?
                    </label>
                    
                    <textarea class="w-100 mt-2 border-2 border-indigo-200 br-input-normal input-base-padding min-height-textarea" 
                        :ref="(el) => (textAreas.currentlyReadingTextArea = el)"
                        :style="{ 'height':  heights[Bookshelves.CURRENTLY_READING.prefix] + 'px' }"
                        :name="Bookshelves.CURRENTLY_READING.prefix"
                        id="currentlyReading"
                        v-model="moveToSelectedShelfData.note" 
                        @input="throttledScrollHeightForTextArea(textAreas.currentlyReadingTextArea)"
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
                <div class="mt-5 place-content-center">
                    <button type="button" class="btn btn-submit small">
                        Move to shelf
                    </button>
                    
                    <label class="flex items-center gap-2 mt-5" for="removeFromCurrentShelf">
                        <input type="checkbox" v-model="moveToSelectedShelfData.isRemovingFromCurrentShelf">
                        <span class="text-sm text-stone-500">Remove this book from the current shelf</span>
                    </label>
                </div>
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
                <span>Click on a book to edit</span> 
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
import { ref, computed, watch, onMounted, toRaw, defineExpose } from 'vue';
import { useRoute } from 'vue-router';
import SortableBook from './SortableBook.vue';
import IconExit from '../../svg/icon-exit.vue';
import { db } from '../../../services/db';
import { urls } from '../../../services/urls';
import { Bookshelves } from '../../../models/bookshelves';
import { helpersCtrl } from '../../../services/helpers';
import CreateUpdateForm from '../createPosts/update/createUpdateForm.vue';

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
    // Heights should only increase, not decrease if the new height is less than the current height - don't set it.
    if (refEl.name === Bookshelves.CURRENTLY_READING.prefix) {
        if (heights.value[Bookshelves.CURRENTLY_READING.prefix] < refEl.scrollHeight) {
            heights.value[Bookshelves.CURRENTLY_READING.prefix] = refEl.scrollHeight;
        }
    } 

    if (refEl.name === Bookshelves.FINISHED_READING.prefix) {
        if (heights.value[Bookshelves.FINISHED_READING.prefix] < refEl.scrollHeight) {
            heights.value[Bookshelves.FINISHED_READING.prefix] = refEl.scrollHeight;
        }
    }

    if (refEl.name === Bookshelves.WANT_TO_READ.prefix) {
        if (heights.value[Bookshelves.WANT_TO_READ.prefix] < refEl.scrollHeight) {
            heights.value[Bookshelves.WANT_TO_READ.prefix] = refEl.scrollHeight;
        }
    }

    if(refEl.name === 'note_for_shelf') {
        console.log(refEl.scrollHeight)
        if (heights.value[Bookshelves.WANT_TO_READ.note_for_shelf] > refEl.scrollHeight) {
            heights.value[Bookshelves.WANT_TO_READ.note_for_shelf] = refEl.scrollHeight;
        }
    }
}


const throttledScrollHeightForTextArea = debounce(generatedHeightForTextArea, 150, true);
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


async function saveBookNoteForCurrentBook() {
    let _data = {
        book_id: currentBookForOverlay.value.id,
        note_for_shelf: currentBookForOverlay.value.note_for_shelf,
    };

    console.log(_data);

    db.put(urls.rtc.updateBookNoteForShelf(route.params.bookshelf), _data).then((res) => {
        console.log(res);
    });
}


/**
 * @async
 * @description: Wrapper around the Bookshelves.moveBookToShelf function.
 * @param {*} bookshelf - bookshelf id of the shelf you want to move things to.
 */
async function moveToShelf(bookshelf) {
    const authors = toRaw(currentBookForOverlay.value.author_names) || toRaw(currentBookForOverlay.value.authors)
    const book = {
        title: currentBookForOverlay.value.title,
        author_names: authors,
        small_img_url: currentBookForOverlay.value.small_img_url,
        id: currentBookForOverlay.value.id,
        noteForShelf: currentBookForOverlay.value.note_for_shelf,
    }
    let currentShelf = '';
    if (moveToSelectedShelfData.value.isRemovingFromCurrentShelf) {
        currentShelf = route.params.shelf;
    }

    try {
        const response = await Bookshelves.moveBookToShelf(bookshelf, book, currentShelf);
        console.log(response);
    } catch (error) {
        console.error(error);
    }
}
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