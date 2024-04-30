<template>
    <div class="mt-5">
        <div id="collaborator-note">
            <p class="bookshelf-note">
                Collaborators have the ability to add, remove and reorder books.
                You can manage your collaborators here.
            </p>
        </div>

        <BookshelfCollaborator role="creator" :friend="{username: 'michaelfinal.png@gmail.com', role: 'creator'}"/>

        <div class="divider"></div>

        <!-- If user has friends render this shit -->
        <div v-if="friends?.length || paginatedFriends?.length">
            <div class="flex items-center gap-5 justify-center">
                <button type="button"
                    class="collaborator-tab"
                    :class="{'active': currentView === 'close-friends'}"
                    @click="currentView = 'close-friends'"
                >
                    Add friends to your bookshelf
                </button>

                <button type="button"
                    class="collaborator-tab"
                    :class="{'active': currentView === 'search-friends'}"
                    @click="currentView  = 'search-friends'"
                    >
                    <!-- :disabled="friends.length < 5" -->
                    Search for friends
                </button>
            </div>
            
            <div v-if="currentView === 'search-friends'">
                <SearchUsers :friends-only="true"
                    label-above="Friends can be either members or collaborators of your bookshelf."
                    @search-friends-result="(friendData) => searchFriendsResult = friendData"
                />
                
                <ul class="collaborators-list">
                    <li v-for="friend in searchFriendsResult" :key="friend?.id">
                        <BookshelfCollaborator :friend="friend"/>
                    </li>
                </ul>
            </div>

            <ul class="collaborators-list" v-if="currentView === 'close-friends'">
                <li v-for="friend in friends" :key="friend?.id">
                    <BookshelfCollaborator :friend="friend" 
                        @remove-friend-from-suggested="(id) => removeFriendFromSuggested(id)"
                    />
                </li>
            </ul>
            <!-- <PaginationControls @increment="(startEndInts) => setPagination(startEndInts)"/> -->
        </div>

        <!-- What to do if users don't have friends, direct them to either a link generator for sign up that sends a friend request auto  -->
        <div v-else>
            <!-- Only render one of these depending on whether or not users have pending friend requests or not-->
            <div class="collaborator-cta" v-if="pendingFriendCount">
                <h2>You haven't connected with your friends on (name of our app) yet.</h2>
                
                <p>Invite them to join <a href="" class="underline">here.</a> <br/></p>
            </div>

            <div class="collaborator-cta" v-else>
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
import { ref, onMounted, computed } from 'vue';
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
const pendingFriendCount = ref(0);
const currentView = ref('close-friends');
const searchFriendsResult = ref([]);
let hiddenFriends = [];

// Need to add this to our backend somehow for paginating through suggested friends.
const currentPaginationGroupEnd = ref(0);
const currentPaginationGroupStart = ref(5);

// pagination is handled on backend for now.
const setPagination = (startEndInts) => {
    currentPaginationGroupStart.value = startEndInts[0];
    currentPaginationGroupEnd.value = startEndInts[1];
}

async function loadFriends(){
    await db.get(`${urls.user.getFriends(route.params.user)}/?includes_pending=true`).then((res) => {
        friends.value = res.friend_list.filter((friend) => !hiddenFriends.includes(friend.id));
        pendingFriendCount.value = res.pendingCount;
    });
};

function removeFriendFromSuggested(id){
    hiddenFriends.push(id);
    sethiddenUserFromShelfInLS();
    friends.value = friends.value.filter((friend) => friend.id !== id);
};

function sethiddenUserFromShelfInLS(){
    localStorage.set(`${route.params.bookshelf}-${route.params.user}-hidden-friends`, hiddenFriends);
};

onMounted(async () => {
    await loadFriends();
    hiddenFriends = [...localStorage.get(`${route.params.bookshelf}-${route.params.user}-hidden-friends`)];
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

.collaborator-tab {
    padding: var(--padding-sm);
    color: var(--stone-600);
    border-bottom: 1px solid var(--stone-300);
    font-family: var(--fancy-script);
}

.collaborator-tab.active {
    color: var(--indigo-500);
    border-bottom-color: var(--indigo-300);
}
</style>