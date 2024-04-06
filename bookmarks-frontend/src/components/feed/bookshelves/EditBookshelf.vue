<template>
    <section class="edit-bookshelf">
        <div class="bookshelf-heading">
            <div>
                <h1 class="bookshelf-title">{{ bookshelfData?.title || 'Untitled'}}</h1>
                <p class="bookshelf-description">{{ bookshelfData?.description || 'Add a description'}}</p>
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
                {{ bookShelfComponentMap[currentView.value].heading(bookshelfData?.title) }}
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
            <div v-if="currentView.value === 'edit-books'">
                <BookshelfBooks 
                    v-if="bookshelfData?.books?.length"
                    :books="books"
                    :can-reorder="isReorderModeEnabled"
                    :is-reordering="isReordering"
                    :unset-current-book="unsetKey"
                    @send-bookdata-socket="
                        (bookdata) => reorder_books(bookdata)
                    "
                    @cancelled-reorder="cancelledReorder"
                />

                <p v-else class="text-no-books-added">No books have been added to this shelf yet.</p>
                <button 
                    type="button"
                    class="btn add-readers-btn mt-5"    
                    @click="gotToAddBooksAndCreateSocketConnection()"
                >Add now</button>
            </div>

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
import { ref, onMounted, reactive, onBeforeUnmount, toRaw } from 'vue';
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
const bookshelfData = ref(null);
const books = ref([]);
const isReordering = ref(false);
const isReorderModeEnabled = ref(false);
let unsetKey = 0;

const error = ref({
    message: '',
    isShowing: false
});

//  Used to send and reorder data!
// #TODO: Fix fix fix please please please. @kylearbide
function reorder_books(bookData) {
    isReordering.value = true;
    bookData.type = 'reorder';
    // Send data to server
    ws.sendData(bookData);
    console.log(bookData, 'bookData'); 
    isReordering.value = false;
    // Forget what this is used for.
    unsetKey++;
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

async function get_shelf() {
    let { bookshelf } = route.params;
    await db.get(urls.rtc.bookShelfTest(bookshelf)).then((res) => { 
    bookshelfData.value = res.bookshelf
    books.value = res.bookshelf.books
    dataLoaded.value = true;
    });
}

async function addBook(book){
    if(ws.socket?.readyState !== 1){
        error.value.message = 'There was an error adding the book to the bookshelf. Please try again.';
        error.value.isShowing = true;
        // Hide toast manually after three seconds.
        setTimeout(() => {
            error.value.isShowing = false;
        }, 5000);
    }
    
    let data = {
        type: 'add',
        bookshelf_id: route.params.bookshelf,
        user_id: route.params.user,
    };

    // Do this just incase something weird happens with the type of data being emmitted.
    data.book = typeof book === 'proxy' ? toRaw(book) : book;
    data.book.order = books.value.length + 1;
    
    ws.sendData(data);
    // TODO add in endpoint put call for attaching a book to a bookshelf.
    setReactiveProperty(currentView, 'value', 'edit-books');
}

function gotToAddBooksAndCreateSocketConnection(){
    ws.createNewSocketConnection(route.params.bookshelf);
    setReactiveProperty(currentView, 'value', 'add-books');
}

async function enterReorderMode(){
    isReorderModeEnabled.value = true;
    // Probably need a way to edit this so we dont keep things open for long. Can add in an edit btn to the ux
    await ws.createNewSocketConnection(route.params.bookshelf);
}

// This may be tricky to lock out the ws connection, people might try and reconnect to soon after disconnecting.
function cancelledReorder() {
    isReorderModeEnabled.value = false;
    isReordering.value = false;
    ws.unsubscribeFromSocketConnection();
    get_shelf();
}

onMounted(() => {
    // Probably could do a better way to generate link in this file. We can figure out later i guess?
    bookshelfData.value = getBookshelf(route.params.bookshelf);
    get_shelf();
    document.addEventListener('ws-loaded-data', () => {
        console.log('ws data has arrived')
        // Make this the new data!
        books.value.push(ws.books.pop());
        ws.books = [];
    });

    document.addEventListener('ws-connection-error', (e) => {
        error.value.message = e.detail.message;
        error.value.isShowing = true;
        // Hide toast manually after three seconds.
        setTimeout(() => {
            error.value.isShowing = false;
        }, 5000);

        if(ws.socket.readyState === 3) {
            console.log('socket is closed, reconnecting');
            ws.createNewSocketConnection(route.params.bookshelf);
        }
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
        font-family: var(--fancy-script);
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

    .text-no-books-added {
        font-size: var(--font-sm);
        color: var(--stone-600);
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
        font-family: var(--fancy-script);
        font-size: var(--font-2xl);
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