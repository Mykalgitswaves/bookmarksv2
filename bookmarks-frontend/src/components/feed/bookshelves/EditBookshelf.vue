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

        <h3 class="bookshelf-books-heading">
            {{ bookShelfComponentMap[currentView.value].heading('untitled') }}
        </h3>
        <BookshelfBooks 
            v-if="dataLoaded"
            :books="books" 
            @send-bookdata-socket="
                (bookdata) => ws.sendData(bookdata)
            "
        />
        <!-- <Component 
            v-if="dataLoaded"
            :is="bookShelfComponentMap[currentView.value].component()"
            v-bind="bookShelfComponentMap[currentView.value].props"
            v-on="bookShelfComponentMap[currentView.value].events" 
        /> -->
    </section>    
    <div class="mobile-menu-spacer sm:hidden"></div>
</template>
<script setup>
import { ref, onMounted, reactive, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router';
import IconEdit from '../../svg/icon-edit.vue'
import BookshelfBooks from './BookshelfBooks.vue';
import SearchBooks from '../createPosts/searchBooks.vue';
import PlaceholderImage from '../../svg/placeholderImage.vue';
import { 
    getBookshelf, 
    goToBookshelfSettingsPage,
    ws,
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

    const currentView = reactive({value: 'edit-books'});
    const { commanatoredString } = helpersCtrl;

    const bookShelfComponentMap = {
        "edit-books": {
            heading: (bookshelfName) => "Edit books",
            buttonText: 'Add books',
            component: () => BookshelfBooks,
            props: {
                'books': books.value,
            },
            events: {

            }
        },
        "add-books": {
            heading: (bookshelfName) => (`Add books to ${bookshelfName}`),
            buttonText: 'Edit books',
            component: () => SearchBooks,
            props: {},
            events: {
                'book-to-parent': addBook
            } 
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

onMounted(() => {
    // Probably could do a better way to generate link in this file. We can figure out later i guess?
    bookshelf.value = getBookshelf(route.params.bookshelf);
    get_combos();
    // Probably need a way to edit this so we dont keep things open for long. Can add in an edit btn to the ux
    ws.createNewSocketConnection(route.params.bookshelf);
});

onUnmounted(() => {
    ws.unsubscribeFromSocketConnection();
});
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
</style>