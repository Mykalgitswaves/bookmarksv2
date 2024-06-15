<template>
    <KeepAlive>
        <section class="edit-bookshelf">
            <!-- titles descriptions and some buttons -->
            <div class="bookshelf-heading">
                <div>
                    <h1 class="bookshelf-title">{{ bookshelfData?.title || 'Untitled'}}</h1>

                    <p class="bookshelf-description">{{ bookshelfData?.description || 'Add a description'}}</p>
                </div>

                <button
                    v-if="isAdmin"
                    type="button"
                    class="btn edit-btn"
                    @click="goToBookshelfSettingsPage(router, route.params.user, route.params.bookshelf)"
                >
                    <IconEdit/>
                </button>
            </div>

            <!-- More nav controls -->
            <div class="bookshelf-top-toolbar">
                <div v-if="isAdmin">
                    <p v-if="!contributorCount" class="collaborators-note">No contributors have been added to this bookshelf yet</p>
                    <p v-else class="collaborators-note">{{ contributorCount }} contributors added</p>   
                </div>

                <div v-if="isAdmin" class="mt-2 flex">
                    <button
                        type="button"
                        class="btn add-readers-btn"
                        :class="{ 'active': currentView.value === 'add-collaborators'}"
                        @click="setReactiveProperty(currentView, 'value', 'add-collaborators')"
                    >
                        Add contributors
                    </button>

                    <button v-if="currentView.value === 'add-collaborators'"
                        type="button"
                        class="btn add-readers-btn ml-5"
                        :class="{ 'active': currentView.value === 'edit-books'}"
                        @click="setReactiveProperty(currentView, 'value', 'edit-books')"
                    >
                        Add books
                    </button>

                    <div>
                        <button
                            v-if="currentView.value === 'edit-books'"
                            type="button"
                            :class="{ 'active': currentView.value === 'edit-books'}"
                            class="btn add-readers-btn ml-5"
                            @click="gotToAddBooksAndCreateSocketConnection()"
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

            <!-- Where you can manage collaborators, add more to your shelf! -->
            <!-- Keep alive prevents us from having to make the same request every time you click away. -->
            <KeepAlive>
                <BookshelfManageCollaborators 
                    v-if="isAdmin && 
                    currentView.value === 'add-collaborators'
                    && dataLoaded"
                    :bookshelf="bookshelfData"    
                    @added-friend-as-contributor="setContributorCount('+')"
                    @removed-friend-as-contributor="setContributorCount('-')"
                />
            </KeepAlive>

            <!-- This is for editing and reordering controls. -->
            <div v-if="isAdmin && currentView.value === 'edit-books'" class="flex items-center space-between">
                <h3 class="bookshelf-books-heading">
                    {{ bookShelfComponentMap[currentView.value].heading(bookshelfData?.title) }}
                </h3>
                
                <div v-if="currentView.value === 'edit-books' && !isReorderModeEnabled && !isEditingModeEnabled" class="flex gap-2">
                    <button class="btn reorder-btn"
                        :disabled="books.length <= 1"
                        @click="enterReorderMode()"
                    >
                        Reorder
                    </button>

                    <button class="btn reorder-btn"
                        :disabled="books.length <= 1"
                        @click="enterEditMode()"
                    >
                        Edit
                    </button>
                </div>
            </div>

            <div v-if="dataLoaded">
                <div v-if="currentView.value === 'edit-books'">
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

                        <button v-if="isAdmin" 
                            type="button"
                            class="btn add-readers-btn mt-5"    
                            @click="gotToAddBooksAndCreateSocketConnection()"
                        >Add now</button>
                    </div>
                </div>
            </div>

            <!-- Where you search for books for adding -->
            <SearchBooks 
                v-if="isAdmin && currentView.value === 'add-books'"
                @book-to-parent="(book) => addBook(book)"  
            />
        </section>   
    </KeepAlive>
     <!--need this until i can figure out better solush smh.  -->
    <div class="mobile-menu-spacer sm:hidden"></div>

    <!-- Errors -->
    <Transition name="content">
        <ErrorToast v-if="error.isShowing" :message="error.message" :refresh="true"/>
    </Transition>
</template>
<script setup>
import { ref, onMounted, reactive, onBeforeUnmount, toRaw, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import IconEdit from '../../svg/icon-edit.vue';
import BookshelfBooks from './BookshelfBooks.vue';
import BookshelfManageCollaborators from './BookshelfManageCollaborators.vue';
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
const { user } = route.params
const dataLoaded = ref(false);
const bookshelfData = ref(null);
const books = ref([]);
const isReordering = ref(false);
const isReorderModeEnabled = ref(false);
const isEditingModeEnabled = ref(false);
const isAdmin = ref(false);
let unsetKey = 0;

const currentBookCount = computed(() => {
    return books.value.length || 0;
});

const error = ref({
    message: '',
    isShowing: false
});

const currentView = reactive({value: 'edit-books'});
const { commanatoredString } = helpersCtrl;

const bookShelfComponentMap = {
    "edit-books": {
        heading: () => `${currentBookCount.value} books`,
        buttonText: 'Add books',
    },
    "add-books": {
        heading: (bookshelfName) => (`Add books to ${bookshelfName}`),
        buttonText: 'Edit books',
    }
};

//  Used to send and reorder data!
// #TODO: Fix fix fix please please please. @kylearbide
function reorder_books(bookData) {
    isReordering.value = true;
    bookData.type = 'reorder';
    // Send data to server
    ws.sendData(bookData);
    isReordering.value = false;
    // Forget what this is used for.
    unsetKey++;
}

/**
 * @description
 * This function is used to get the bookshelf data from the server.
 */
async function get_shelf() {
    let { bookshelf } = route.params;
    await db.get(urls.rtc.bookShelfTest(bookshelf)).then((res) => { 
        bookshelfData.value = res.bookshelf
        books.value = res.bookshelf.books
        dataLoaded.value = true;
        isAdmin.value = !!(res.bookshelf.created_by === user);
    });
}

/**
 * @description
 * This function is used to add a book to the bookshelf. It will send the data to the ws server
 */
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

/**
 * @description
 * This function is used to navigate to the bookshelf settings page.
 * This function also creates a socket connection if one does not exist.
 */
function gotToAddBooksAndCreateSocketConnection(){
    if(ws.socket?.readyState !== 1 || !ws.socket) {
        ws.createNewSocketConnection(route.params.bookshelf);
    }
    
    setReactiveProperty(currentView, 'value', 'add-books');
}

/**
 * @description
 * This function is used to enter reorder mode. It will create a new socket connection
 * and subscribe to the socket connection.
 */
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

/**
 * @description
 * This function is used to enter edit mode. It will allow users to add tags and delete books.
 */
async function enterEditMode(){
    await ws.createNewSocketConnection(route.params.bookshelf);
    isEditingModeEnabled.value = true;
}

function cancelledEdit(){
    isEditingModeEnabled.value = false;
    ws.unsubscribeFromSocketConnection();
}

/**
 * @description
 * This function is used to remove a book from the bookshelf.
 * @param {string} removed_book_id - The id of the book that is being removed.
 * This function uses a key ref object used as a depencency inside of
 * BookshelfBooks computed function which sets currentBook to null.
 */
function remove_book(removed_book_id){
    let data = {
        type: 'delete',
        target_id: removed_book_id,
        bookshelf_id: route.params.bookshelf,
    };

    ws.sendData(data);
    unsetKey++;
}

onMounted(() => {
    // Probably could do a better way to generate link in this file. We can figure out later i guess?
    bookshelfData.value = getBookshelf(route.params.bookshelf);
    get_shelf();
    document.addEventListener('ws-loaded-data', () => {
        console.log('ws data has arrived')
        // Grab the last added book to the shelf!
        books.value = ws.books;
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

const changedCount = ref(0);
const contributorCount = computed(() => (bookshelfData.value.contributors.length + bookshelfData.value.members.length - 1) + changedCount.value);

function setContributorCount(operator){
    if(operator === '+'){
        changedCount.value += 1;
    } else {
        changedCount.value -= 1;
    }

}
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