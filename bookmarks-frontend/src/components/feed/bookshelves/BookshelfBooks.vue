<template>
    <ul class="bookshelf-books" ref="books" v-if="books.length">
        <li v-for="book in books" :key="index" class="bs-b-wrapper">
            <SortableBook
                :order="book.order"
                :id="book.id"
                :bookTitle="book.bookTitle"
                :author="book.author"
                :imgUrl="book.imgUrl"
                :sort-target="currentBook"
                @set-sort="(data) => setSort(data)"
                @swapped-with="(book_data) => swappedWithHandler(book_data)"
            />
        </li>
    </ul>

    <teleport v-if="sortTarget !== null" to="body">
        <div class="sorting-footer">
            <h3 
                v-if="currentBook"
                class="s-f--current-book"
            >
                {{ selectedBookToBeMoved }}
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
import SortableBook from './SortableBook.vue';

const props = defineProps({
    books: {
        type: Array,
        required: false,
        default: [],
    },
    isReordering: {
        type: Boolean,
    }
});

const emit = defineEmits(['send-bookdata-socket']);

// need this to handle multiple sorts at a time.
const sortTarget = ref(null);

// This is what will be sent via websocket over the wire.
const bookdata = reactive({
    book_id: null,
    prev_book_id: null,
    next_book_id: null,
});

const currentBook = ref({});

const selectedBookToBeMoved = computed(() => 
    `#${currentBook.value.order} ${currentBook.value.bookTitle}`
);

function setSort(nameData) {
    console.assert(nameData !== (null || undefined))
    bookdata.book_id = nameData;
    sortTarget.value = props.books.find(b = b.id === nameData.id);
};

function swappedWithHandler(book_data) {
    console.log(book_data);
    let prev = props.books.find((book) => 
        book.order === book_data.order - 1
    );
    let next = props.books.find((book) => 
        book.order === book_data.order + 1
    );

    bookdata.prev_book_id = prev ? prev.id : null;
    bookdata.next_book_id = next ? next.id : null;
    emit('send-bookdata-socket', bookdata);
};

function resetSort() {
    sortTarget.value = null;
    Object.keys(bookdata).forEach((key) => bookdata[key] = null);
}
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