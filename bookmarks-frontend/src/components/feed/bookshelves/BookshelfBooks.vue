<template>
    <ul class="bookshelf-books" ref="books" v-if="books.length">
        <li v-for="(book, index) in books" :key="index" class="bs-b-wrapper">
            <SortableBook
                :order="index"
                :id="book?.id"
                :bookTitle="book?.bookTitle"
                :author="book?.author"
                :imgUrl="book?.imgUrl"
                :next-book="books[index + 1]"
                :prev-book="books[index - 1]"
                :current-book="currentBook"
                @set-sort="(data) => setSort(data)"
                @swapped-with="(data) => swappedWithHandler(data)"
            />
        </li>
    </ul>

    <teleport v-if="currentBook !== null || canReorder" to="body">
        <div class="sorting-footer">
            <div v-if="currentBook" class="s-f-book">
                <img :src="currentBook.imgUrl" class="s-f--current-book-img" alt="">

                <h3 class="s-f--current-book">
                {{ selectedBookToBeMoved }}
                </h3>
            </div>

            <h3 v-else>
                Click on a book to reorder
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
import { ref, computed, reactive } from 'vue';
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
    }
});

const route = useRoute();
const { user } = route.params;
const emit = defineEmits(['send-bookdata-socket', 'cancelled-reorder']);

// This is what will be sent via websocket over the wire.
const bookdata = reactive({
    target_id: null,
    previous_book_id: null,
    next_book_id: null,
    author_id: user,
});

const currentBook = ref(null);

const selectedBookToBeMoved = computed(() => 
    `#${currentBook.value.order} ${currentBook.value.bookTitle}`
);

// Used to set the current target
function setCurrentBook(booKData) {
    currentBook.value = props.books.find((b)=> b.id === booKData);
}

// early step of swap, sets currentBook.
function setSort(bookData) {
    if(props.canReorder){
        console.assert(bookData !== (null || undefined));
        bookdata.target_id = bookData;
        setCurrentBook(bookData);
    }
};

// When someone cancels.
function resetSort() {
    currentBook.value = null;
    //  Reset all properties of this object.
    bookdata.value = {
        target_id: null,
        previous_book_id: null,
        next_book_id: null,
        author_id: user
    };
    emit('cancelled-reorder')
};

// Setting up data needed for EditBookshelf's reorder function.
function swappedWithHandler(book_data) {
    let prev = props.books.find((book) => 
        book.order === book_data.order
    );

    let next = props.books.find((book) => 
        book.order === book_data.order + 1
    );

    bookdata.previous_book_id = prev ? prev.id : null;
    bookdata.next_book_id = next ? next.id : null;


    emit('send-bookdata-socket', bookdata);
};
</script>

<style scoped lang="scss">
    .bookshelf-books {
        display: grid;
        padding-top: var(--padding-sm);
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