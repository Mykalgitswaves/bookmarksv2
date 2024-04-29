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
        <!-- If user has friends render this shit -->
        <div v-if="friends?.length">
            <div class="flex items-center gap-2">
                <button type="button"
                    class="collaborator-tab"
                    @click="currentView = 'close-friends'"
                >
                    Add friends to your bookshelf
                </button>

                <button type="button"
                    class="collaborator-tab"
                    @click="currentView  = 'search-friends'"
                >

                </button>
            </div>
            
            <SearchUsers v-if="currentView === 'search-friends'"
                :friends-only="true"
                label-above="Friends can be either members or collaborators of your bookshelf."
            />

            <ul class="collaborators-list">
                <li>
                    <BookshelfCollaborator />
                </li>
            </ul>
        </div>

        <!-- What to do if users don't have friends, direct them to either a link generator for sign up that sends a friend request auto  -->
        <div v-else>
            <!-- Only render one of these depending on whether or not users have pending friend requests or not-->
            <div class="collaborator-cta">
                <h2>You haven't connected with your friends on (name of our app) yet.</h2>
                
                <p>Invite them to join <a href="" class="underline">here.</a> <br/></p>
            </div>

            <div class="collaborator-cta">
                <h2>You haven't connected with your friends on (name of our app) yet.</h2>
                
                <p>Accept your requests to add a friend to this bookshelf</p>

                <a href="" class="underline">
                    Accept friend requests
                </a>
            </div>
        </div>
    </div>
</template>

<script setup>
import BookshelfCollaborator from './BookshelfCollaborator.vue';
import SearchUsers from '../social/SearchFriends.vue';
import { ref, onMounted } from 'vue';
import { db } from '../../../services/db';
import { urls } from '../../../services/urls';
import { useRoute } from 'vue-router';

const props = defineProps({
    bookshelf: {
        type: Object,
        required: true,
    },
});

const route = useRoute();
const friends = ref([]);

async function loadFriends(){
    await db.get(`${urls.user.getFriends(route.params.user)}/?includes_pending=true`).then((res) => {
        friends.value = res;
    });
};

onMounted(async () => {
    await loadFriends();
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