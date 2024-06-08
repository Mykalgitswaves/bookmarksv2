<template>
    <section class="edit-bookshelf">
        <div class="bookshelf-heading">
            <div>
                <h1 class="bookshelf-title">{{ bookshelfData?.title || 'Untitled'}}</h1>

                <p class="bookshelf-description">{{ bookshelfData?.description || 'Add a description'}}</p>
            </div>

            <button
                type="button"
                class="btn edit-btn b-light text-stone-200"
                @click="goToBookshelfSettingsPage(router, route.params.user, route.params.bookshelf)"
            >
                <IconEdit/>
            </button>
        </div>

        <div class="bookshelf-top-toolbar">
            <div class="mt-2 flex">
                <!-- v-if="isAdmin" -->
                <button
                    type="button"
                    class="btn add-readers-btn"
                    @click="currentView = 'edit-books'"
                >
                    Edit books
                </button>

                <button 
                    type="button"
                    class="btn add-readers-btn ml-5"
                    @click="currentView = 'add-books'"
                >
                    Add books
                </button>
            </div>
        </div>

        <!-- Add and view books -->
        <div v-if="loaded && currentView === 'edit-books'" class="mt-5">
            <BookshelfBooks 
                v-if="books?.length"
                :is-admin="isAdmin"
                :books="books"
                :can-reorder="isReorderModeEnabled"
                :is-editing="isEditingModeEnabled"    
                :is-reordering="isReordering"
                :unset-current-book="unsetKey"
                @send-bookdata-socket="
                    (bookdata) => reorder_books(bookdata)
                "
                @removed-book="(removed_book_id) => remove_book(removed_book_id)"
                @cancelled-reorder="cancelledReorder"
                @cancelled-edit=cancelledEdit
            />

            <div v-else>
                <p class="text-no-books-added">No books have been added to this shelf yet.</p>

                <button 
                    type="button"
                    class="btn add-readers-btn mt-5"    
                    @click="currentView = 'add-books'"
                >Add now</button>
            </div>
        </div>

        <!-- Where you search for books for adding -->
        <SearchBooks 
            v-if="currentView === 'add-books' && currentBook === null"
            :centered="true"
            @book-to-parent="(book) => setCurrentBook(book)"
        />

        <div v-if="currentBook" class="ml-auto mr-auto mt-10 w-80">
            <BookSearchResults :data="[currentBook]" :disabled="true"/>

            <div class="mb-5 text-center">
                <span class="text-stone-600 fancy">Reason you are adding this book</span>
                
                <textarea class="add-book-note" v-model="currentBook.note_for_shelf" name="" id="" cols="30" rows="5"/>
            </div>

            <div class="w-100 gap-2 flex items-center">
                <button type="button" class="btn btn-submit w-50" @click="addBookHandler(currentBook)">Add book</button>

                <button type="button" class="btn btn-ghost w-50" @click="currentBook = null">Cancel</button>
            </div>
        </div>
    </section>

    <div class="mobile-menu-spacer sm:hidden"></div>
</template>
<script setup>
import { onMounted, ref, toRaw} from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getWantToReadshelfPromise, addBook } from './wantToRead.js';
import { goToBookshelfSettingsPage } from '../bookshelves/bookshelvesRtc';
import { urls } from "../../../services/urls";
import { db } from "../../../services/db";
import IconEdit from '../../svg/icon-edit.vue';
import BookshelfBooks from './BookshelfBooks.vue';
import SearchBooks from '../createPosts/searchBooks.vue';
import BookSearchResults from '../../create/booksearchresults.vue';


const route = useRoute();
const router = useRouter();
const { user } = route.params;
const bookshelfData = ref(null);
const isAdmin = ref(false);
const currentView = ref('edit-books');
const loaded = ref(false);
const books = ref([]);
const currentBook = ref(null);

onMounted(async() => {
    const wantToReadShelfPromise = await getWantToReadshelfPromise(user);
    Promise.all([wantToReadShelfPromise]).then(([wantToReadShelf]) => {
        bookshelfData.value = wantToReadShelf.bookshelf;
        books.value = wantToReadShelf.bookshelf.books;
        isAdmin.value = !!wantToReadShelf.bookshelf.created_by_current_user;
        loaded.value = true;
    });
});

function setCurrentBook(book) {
    currentBook.value = book;
    currentBook.value.note_for_shelf = '';
    console.log(currentBook.value)
}

async function addBookHandler(book) {
    book = typeof book === 'proxy' ? toRaw(book) : book;
    
    let bookObject = {
        title: book.title,
        id: book.id,
        small_img_url: book.small_img_url,
        author_names: book.author_names,
        note_for_shelf: book.note_for_shelf,
    };

    books.value.push({book: bookObject});

    db.put(
        urls.rtc.quickAddBook('want_to_read'),
        { book: bookObject }
    ).then((res) => {
        currentBook.value = null;
        currentView.value = 'edit-books';
    });
}
</script>
<style scoped>
.add-book-note {
    width: 100%;
    border: none;
    appearance: none;
    resize: none;
    color: var(--stone-600);
    margin-right: 4px;
    margin-top: 8px;
    padding-top: 8px;
    padding-left: 8px;
    background-color: transparent;
    border: 1px dotted var(--stone-200);
    border-radius: var(--radius-sm);
}

.add-book-note:focus {
    border-color: var(--indigo-500);
    outline: none;
}
</style>