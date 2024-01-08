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
            <button
                type="button"
                class="btn add-readers-btn"
            >
                Add readers
            </button>
        </div>
        <BookshelfBooks :books="[{}, {}]"/>
    </section>    
</template>
<script setup>
    import { ref, computed, onMounted } from 'vue'
    import { useRoute, useRouter } from 'vue-router';
    import BookshelfBooks from './BookshelfBooks.vue';
    import IconEdit from '../../svg/icon-edit.vue'
    import PlaceholderImage from '../../svg/placeholderImage.vue';
    import { getBookshelf, goToBookshelfSettingsPage } from './bookshelvesRtc';
    const route = useRoute();
    const router = useRouter();

    const bookshelf = ref(null);

    onMounted(() => {
        bookshelf.value = getBookshelf(route.params.bookshelf);
    })
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
</style>