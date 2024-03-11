<template>
    <section class="edit-bookshelf">
        <div class="bookshelf-heading">
            <div>
                <h1 class="bookshelf-title">{{ bookshelf?.title || 'Untitled'}}</h1>
                <p class="bookshelf-description">{{ bookshelf?.description || 'Add a description'}}</p>
            </div>
            <button
                type="button"
                class="btn edit-btn"
                @click="goToBookshelfSettingsPage(router, route.params.user, route.params.bookshelf)"
            >
                <IconEdit/>
            </button>
        </div>
        <div class="bookshelf-top-toolbar">
            <div v-if="!collaborators?.length" class="flex items-end">
                <PlaceholderImage class="extra small-profile-image"/>
                <p class="no-collaborators-note">No collaborators added to this bookshelf yet</p>
            </div>

            <div class="mt-2 flex space-between">
                <button
                    type="button"
                    class="btn add-readers-btn"
                >
                    Add readers
                </button>

                <div>
                    <button
                        v-if="currentView.value === 'edit-books'"
                        type="button"
                        class="btn add-readers-btn ml-5"
                        @click="setReactiveProperty(currentView, 'value', 'add-books')"
                    >
                        {{ bookShelfComponentMap[currentView.value].buttonText }}
                    </button>

                    <button
                        v-if="currentView.value === 'add-books'"
                        type="button"
                        class="btn add-readers-btn ml-5"
                        @click="setReactiveProperty(currentView, 'value', 'edit-books')"
                    >
                        {{ bookShelfComponentMap[currentView.value].buttonText }}
                    </button>
                </div>
            </div>
        </div>

        <div class="flex items-center space-between">
            <h3 class="bookshelf-books-heading">
                {{ bookShelfComponentMap[currentView.value].heading('untitled') }}
            </h3>
            
            <button
                v-if="currentView.value === 'edit-books' && !isReorderModeEnabled"
                class="btn reorder-btn"
                @click="enterReorderMode()"
            >
                <IconReorder class="ninety-deg"/>
            </button>
        </div>

        <div v-if="dataLoaded">
            <BookshelfBooks 
                v-if="currentView.value === 'edit-books'"
                :books="books"
                :can-reorder="isReorderModeEnabled"
                :is-reordering="isReordering"
                @send-bookdata-socket="
                    (bookdata) => reorder_books(bookdata)
                "
                @cancelled-reorder="cancelledReorder()"
            />

            <SearchBooks 
                v-if="currentView.value === 'add-books'"
                @book-to-parent="(book) => addBook(book)"  
            />
        </div>
    </section>    
    <div class="mobile-menu-spacer sm:hidden"></div>

    <Transition name="content">
        <ErrorToast v-if="error.isShowing" :message="error.message" :refresh="true"/>
    </Transition>

</template>
<script setup>
import { ref, onMounted, reactive, onBeforeUnmount } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import IconEdit from '../../svg/icon-edit.vue';
import IconReorder from '../../svg/icon-reorder.vue';
import BookshelfBooks from './BookshelfBooks.vue';
import SearchBooks from '../createPosts/searchBooks.vue';
import PlaceholderImage from '../../svg/placeholderImage.vue';
import ErrorToast from '../../shared/ErrorToast.vue';
import { 
    getBookshelf, 
    goToBookshelfSettingsPage,
    ws,
    removeWsEventListener,
} from './bookshelvesRtc';
import { setReactiveProperty } from '../../../services/helpers';
import { helpersCtrl } from '../../../services/helpers'
import { urls } from '../../../services/urls';
import { db } from '../../../services/db';

const route = useRoute();
const router = useRouter();
const dataLoaded = ref(false);
const bookshelf = ref(null);
const books = ref([]);
const isReordering = ref(false);
const isReorderModeEnabled = ref(false);

const error = ref({
    message: '',
    isShowing: false
});

//  Used to send and reorder data!
function reorder_books(bookData) {
    isReordering.value = true;

    const { target_id, previous_book_id, next_book_id } = bookData;

    // Find the current, previous, and next books
    const curr = books.value.find(b => b.id === target_id);
    const prev = previous_book_id ? books.value.find(b => b.id === previous_book_id) : null;
    const next = next_book_id ? books.value.find(b => b.id === next_book_id) : null;

    // Early exit if we can't find the current book or both previous and next books
    if (!curr || (!prev && !next)) {
        isReordering.value = false;
        return;
    }

    // Remove current book from the list
    const indexOfCurr = books.value.indexOf(curr);
    books.value.splice(indexOfCurr, 1);

    // Find the index where the current book should be inserted
    let insertIndex = 0; // Default to beginning of the list
    if (prev && next) {
        // If both previous and next books exist, insert between them
        const indexOfPrev = books.value.indexOf(prev);
        const indexOfNext = books.value.indexOf(next);
        insertIndex = indexOfPrev + 1;
        if (indexOfNext === indexOfPrev + 1) {
            // If next book is right after previous book, insert after previous book
            insertIndex = indexOfPrev + 1;
        } else {
            // If there's a gap between previous and next books, insert before next book
            insertIndex = indexOfNext;
        }
    } else if (prev) {
        // If only previous book exists, insert after previous book
        insertIndex = books.value.indexOf(prev) + 1;
    } // If only next book exists, insert before next book (default to beginning of the list)

    // Insert the current book at the determined index
    books.value.splice(insertIndex, 0, curr);

    // Update the order of each book
    books.value.forEach((b, index) => b.order = index);

    // Send data to server
    ws.sendData(bookData);

    isReordering.value = false;
}

const currentView = reactive({value: 'edit-books'});
const { commanatoredString } = helpersCtrl;

const bookShelfComponentMap = {
    "edit-books": {
        heading: () => "Reorder books",
        buttonText: 'Add books',
    },
    "add-books": {
        heading: (bookshelfName) => (`Add books to ${bookshelfName}`),
        buttonText: 'Edit books',
    }
};

async function get_combos() {
    await db.get(urls.rtc.bookShelfTest('new')).then((res) => { 
    bookshelf.value = res.bookshelf
    books.value = res.bookshelf.books
    dataLoaded.value = true;
    });
}

function addBook(book){
    let props = {
        id: book.id,
        order: books.value.length++, 
        bookTitle: book.title,
        author: commanatoredString(book.authorNames),
        imgUrl: book.imgUrl
    };

    books.value.push(props);
    // TODO add in endpoint put call for attaching a book to a bookshelf.
    setReactiveProperty(currentView, 'value', 'edit-books');
}

async function enterReorderMode(){
    isReorderModeEnabled.value = true;
    // Probably need a way to edit this so we dont keep things open for long. Can add in an edit btn to the ux
    await ws.createNewSocketConnection(route.params.bookshelf);
}

// This may be tricky to lock out the ws connection, people might try and reconnect to soon after disconnecting.
function cancelledReorder() {
    isReorderModeEnabled.value = false;
    ws.unsubscribeFromSocketConnection();
}

onMounted(() => {
    
    // Probably could do a better way to generate link in this file. We can figure out later i guess?
    bookshelf.value = getBookshelf(route.params.bookshelf);
    get_combos();
    document.addEventListener('ws-loaded-data', () => {
        console.log('ws data has arrived')
        // Make this the new data!
        books.value = ws.books;
    });

    document.addEventListener('ws-connection-error', (e) => {
        error.value.message = e.detail.message;
        error.value.isShowing = true;
        // Hide toast manually after three seconds.
        setTimeout(() => {
            error.value.isShowing = false;
        }, 5000);
    });
});

// Need this for regular navigation.
onBeforeUnmount(() => {
    ws.unsubscribeFromSocketConnection();
    removeWsEventListener();
});

// Need to send close frame for websocket
window.onbeforeunload = () => {
    ws.unsubscribeFromSocketConnection();
    removeWsEventListener();
};
</script>
<style scoped>

    .edit-bookshelf {
        margin-left: auto;
        margin-right: auto;
        max-width: 880px;
        padding-left: var(--padding-sm);
        padding-right: var(--padding-sm);
    }
    
    @media screen and (max-width: 550px) {
        .edit-bookshelf {
            padding-left: 0;
            padding-right: 0;
        }   
    }

    .bookshelf-heading {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .bookshelf-title {
        font-size: var(--font-4xl);
        font-weight: 500;
        color: var(--stone-700);
        line-height: 1.5;        
    }

    .bookshelf-description {
        font-size: var(--font-lg);
        color: var(--stone-500);
        line-height: 1.2;
    }

    .bookshelf-top-toolbar {
        padding-top: calc(2 * var(--padding-md));
        padding-bottom: var(--padding-sm);
        border-bottom: 1px solid var(--stone-200);
        justify-content: space-between;
        display: flex;
        flex-wrap: wrap;
        line-break: anywhere;
        row-gap: 14px;
        column-gap: 14px;
    }


    .no-collaborators-note {
        font-size: var(--font-sm);
        color: var(--stone-600);
    }

    .add-readers-btn {
        border: 1px solid var(--stone-300);
        font-size: var(--font-sm);
        transition: var(--transition-short);
    }

    .add-readers-btn:hover {
        transform: scale(1.02);
    }

    .bookshelf-books-heading {
        font-size: var(--font-xl);
        font-weight: 500;   
        margin-top: var(--padding-sm);
        color: var(--stone-600);
    }

    .reorder-btn {
        border: 1px solid var(--stone-200);
        padding: var(--padding-sm);
        margin-top: var(--padding-md);
    }
</style>