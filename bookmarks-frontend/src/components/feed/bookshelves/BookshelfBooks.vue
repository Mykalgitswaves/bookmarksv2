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
                :author="book?.author_names"
                :imgUrl="book?.small_img_url"
                :next-book="books[index + 1]"
                :prev-book="books[index - 1]"
                :current-book="currentBook"
                :index="index"
                :is-editing="isEditing"
                @set-sort="(data) => setSort(data)"
                @swapped-with="(data) => swappedWithHandler(data)"
                @removed-book="$emit('removed-book', $event)"
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
</template>
<script setup>
import { ref, computed, reactive, watch } from 'vue';
import { useRoute } from 'vue-router';
import SortableBook from './SortableBook.vue';

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
});

const route = useRoute();
const { user } = route.params;
const emit = defineEmits(['send-bookdata-socket', 'cancelled-reorder']);

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

</script>

<style scoped lang="scss">
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