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
            <div class="mt-2 flex w-100">
                <!-- v-if="isAdmin" -->
                <div class="w-80"> 
                    <button
                        type="button"
                        class="btn add-readers-btn"
                        :class="{'active': currentView === 'view-books'}"
                        @click="currentView = 'view-books'"
                    >
                        View bookshelf
                    </button>

                    <button 
                        type="button"
                        class="btn add-readers-btn ml-5"
                        :class="{'active': currentView === 'add-books'}"
                        @click="currentView = 'add-books'"
                    >
                        Add books to shelf
                    </button>
                </div>

                <button
                    type="button"
                    class="btn btn-ghost btn-icon pb-0 pblock-sm pt-0 ml-auto whitespace-nowrap"
                    @click="Bookshelves.enterEditingMode(route.params.bookshelf, isEditingModeEnabled)"
                >
                    <IconEdit />
                    <span class="hidden-on-mobile text-sm">Edit books</span>
                </button>  
                
            </div>
        </div>

        <!-- Add and view books -->
        <div v-if="loaded && currentView === 'view-books'" class="mt-5">
            <BookshelfBooks 
                v-if="books?.length"
                ref="bookshelfBooks"
                :unique="Bookshelves.CURRENTLY_READING.prefix"
                :is-admin="isAdmin"
                :books="books"
                :is-editing="isEditingModeEnabled.value"    
                :is-reordering="isReordering"
                :unset-current-book="unsetKey"
                @send-bookdata-socket="
                    (bookdata) => reorder_books(bookdata)
                "
                @removed-book="(removed_book_id) => removeBookFromShelf(removed_book_id)"
                @cancelled-edit="Bookshelves.exitEditingMode(isEditingModeEnabled)"
                @post-update="(updatePayload) => createUpdatePost(updatePayload)"
            >
            </BookshelfBooks>

            <div v-else>
                <p class="text-no-books-added">No books have been added to this shelf yet.</p>

                <button 
                    type="button"
                    class="btn underline text-indigo-500 mt-5"    
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
                <button type="button" class="btn btn-submit w-50" @click="
                    Bookshelves.addBookHandler(currentBook, books, 'currently_reading'); 
                    currentBook = null; 
                    currentView = 'view-books'"
                >Add book
                </button>

                <button type="button" class="btn btn-ghost w-50" @click="currentBook = null">Cancel</button>
            </div>
        </div>
    </section>

    <!-- Errors -->
    <Transition name="content">
        <ErrorToast v-if="error?.isShowing" :message="error.message" :refresh="true"/>
    </Transition>

    <Transition name="content">
        <SuccessToast v-if="toast" :toast="toast" /> 
    </Transition>

    <div class="mobile-menu-spacer sm:hidden"></div>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import { db } from '../../../services/db';
import { urls } from '../../../services/urls';
import { useRoute } from 'vue-router';
import { Bookshelves } from '../../../models/bookshelves';
import { ws, removeWsEventListener } from '../bookshelves/bookshelvesRtc'
import BookshelfBooks from './BookshelfBooks.vue';
import SearchBooks from '../createPosts/searchBooks.vue';
import BookSearchResults from '../../create/booksearchresults.vue';
import ErrorToast from '../../shared/ErrorToast.vue';
import SuccessToast from '../../shared/SuccessToast.vue';
// // // // // // // // // // // // // 
// -- -- -- --- Routes --- -- -- -- // 
const route = useRoute();
const { user } = route.params;
// // // // // // // // // // // // // 


// // // // // // // // // // // // // 
// - View variables and booleans -  // 
const currentView = ref('view-books');
const loaded = ref(false);
const isEditingModeEnabled = ref({value: false});
const bookshelfData = ref(null);
const currentBook = ref(null);
const error = ref({
    isShowing: false,
    message: '',
});
const books = ref([]);
const isAdmin = ref(false);
let unsetKey = 0;
const bookshelfBooks = ref(null);
const toast = ref(null);
// // // // // // // // // // // // //


// Initial load for shit inside // //
// onMounted so stuff can break and /
// not ruin app, it just returns // /
// // // // // // // // // // // // //
onMounted(async () => {
    db.get(urls.rtc.getCurrentlyReading(user))
    .then((res) => {
        bookshelfData.value = res.bookshelf;
        books.value = res.bookshelf.books;
        isAdmin.value = !!(user === res.bookshelf.created_by)
        loaded.value = true;
    }).catch((err) => {
        console.error(err)
    });

    // Web socket related listeners
    document.addEventListener('ws-loaded-data', (e) => {
        books.value = ws.books;
    });

    document.addEventListener('ws-connection-error', (e) => {
        error.value.message = e.detail.message;
        error.value.isShowing = true;
        // Hide toast manually after three seconds.
        setTimeout(() => {
            error.value.isShowing = false;
        }, 5000);

        if(ws.socket?.readyState === 3) {
            console.warn('socket is closed, reconnecting');
            ws.createNewSocketConnection(route.params.bookshelf);
        }
    });
});


// -- -- --- Functions --- -- -- // 
// // // // // // // // // // // //

function setCurrentBook(book) {
    currentBook.value = book;
    currentBook.value.note_for_shelf = '';
} 

async function createUpdatePost(updatePayload) { 
    await db.post(urls.reviews.update, updatePayload, true).then((res) => {
       bookshelfBooks.value.currentBook = null;
       toast.value = Bookshelves.createToastForPost(res.data);
  });
}

function removeBookFromShelf(removed_book_id) {
    try {
        ws.sendData({
            type: 'delete',
            target_id: removed_book_id,
        });
    } catch (error) {
        console.error(error);
    }
}
</script>
