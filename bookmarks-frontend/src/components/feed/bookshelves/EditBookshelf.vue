<template>
    <section class="edit-bookshelf">
        <div class="bookshelf-heading">
            <div>
                <h1 class="bookshelf-title">{{ bookshelfTitle || 'Untitled'}}</h1>
                <p class="bookshelf-description">{{ bookshelfdescription || 'Add a description'}}</p>
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
                    @click="setReactiveProperty(currentView, 'value', 'edit-books')"
                >
                    Add readers
                </button>
                <button
                    type="button"
                    class="btn add-readers-btn ml-5"
                    @click="setReactiveProperty(currentView, 'value', 'add-books')"
                >
                    Add books
                </button>
            </div>
        </div>

        <h3 class="bookshelf-books-heading">
            {{ bookShelfComponentMap[currentView.value].heading('untitled') }}
        </h3>

        <Component 
            :is="bookShelfComponentMap[currentView.value].component()"
            v-bind="bookShelfComponentMap[currentView.value].events" 
        />
    </section>    
    <div class="mobile-menu-spacer sm:hidden"></div>
</template>
<script setup>
    import { ref, onMounted, reactive } from 'vue'
    import { useRoute, useRouter } from 'vue-router';
    import IconEdit from '../../svg/icon-edit.vue'
    import PlaceholderImage from '../../svg/placeholderImage.vue';
    import { 
        getBookshelf, 
        goToBookshelfSettingsPage,
        bookShelfComponentMap
    } from './bookshelvesRtc';
    import { setReactiveProperty } from '../../../services/helpers';
    const route = useRoute();
    const router = useRouter();
    const bookshelf = ref(null);
    
    const books = ref([]);

    const currentView = reactive({value: 'edit-books'});

    function addBook(book){
        books.value.push(book);
    }

    onMounted(() => {
        bookshelf.value = getBookshelf(route.params.bookshelf);
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