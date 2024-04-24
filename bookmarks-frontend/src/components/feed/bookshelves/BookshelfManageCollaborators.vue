<template>
    <div class="mt-5">
        <div id="collaborator-note">
            <p class="bookshelf-note">
                Collaborators have the ability to add, remove and reorder books.
                You can manage your collaborators here.
            </p>
        </div>

        <BookshelfCollaborator role="creator"/>

        <div class="divider"></div>
        
        <SearchUsers :friends-only="true"
            label-above="Friends can be either members or collaborators of your bookshelf."
        />

        <ul class="collaborators-list">
            <li>
                <BookshelfCollaborator />
            </li>
        </ul>

        <ul>

        </ul>
    </div>
</template>

<script setup>
import BookshelfCollaborator from './BookshelfCollaborator.vue';
import SearchUsers from '../social/SearchFriends.vue';

const props = defineProps({
    bookshelf: {
        type: Object,
        required: true,
    },
});

console.log(props.bookshelf);

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