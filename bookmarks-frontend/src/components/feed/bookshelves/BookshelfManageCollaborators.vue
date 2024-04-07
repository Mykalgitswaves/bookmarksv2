<template>
    <div class="mt-5">
        <BookshelfCollaborator/>

        <div id="collaborator-note">
            <p class="bookshelf-note">
                Collaborators have the ability to add, remove and reorder books.
                You can manage your collaborators here.
            </p>
        </div>

        <ul class="collaborators-list">
            <li>
                <BookshelfCollaborator />
            </li>
        </ul>

        <ul>

        </ul>
    </div>
</template>

<script>
import { defineProps } from 'vue';
import BookshelfCollaborator from './BookshelfCollaborator.vue';
import SearchBooks from '../createPosts/searchBooks.vue';

const props = defineProps({
    bookshelf: {
        type: Object,
        required: true,
    },
});

</script>
<style scoped>
.bookshelf-note {
    font-size: var(--font-sm);
    color: var(--stone-500);
    margin-bottom: var(--margin-md);
    margin-left: auto;
    margin-left: right;
    text-align: start;
}

.collaborators-list {
    margin-top: var(--margin-md);
    margin-bottom: var(--margin-md);
}
</style>