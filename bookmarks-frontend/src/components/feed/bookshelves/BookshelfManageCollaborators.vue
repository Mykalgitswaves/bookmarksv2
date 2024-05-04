<template>
    <div class="mt-5">
        <button type="button" 
            class="btn flex gap-2 mb-2 pl-0" 
            @click="modals.showInfoModal = !modals.showInfoModal"
        >
            <IconInfo />

            learn more about contributors
        </button>

        <div>
            <div id="collaborator-note" v-if="modals.showInfoModal">
                <p class="bookshelf-note">
                    Contributors have the ability to add, remove and reorder books.
                    You can manage your contributors here. bookshelves can have a maximum limit of 5 contributors.
                    Members are able to view books but cannot edit bookshelves.
                </p>
            </div>
        </div>
        <div>
            <h2 class="">Owner</h2>

            <BookshelfCollaborator 
                v-if="bookshelfOwner"
                :role="bookshelfOwner?.role"
                :friend="bookshelfOwner" 
            />

            <div class="divider"></div>

            <!-- All contributors of shelf. -->
            <h2><span v-if="bookshelfContributors?.length">{{ bookshelfContributors.length }}</span> Contributors</h2>

            <ul class="collaborators-list">
                <li v-for="friend in bookshelfContributors" :key="friend?.id">
                    <BookshelfCollaborator role="contributor"
                        :friend="friend" 
                        :bookshelf-id="route.params.bookshelf"
                        :current-user-is-admin="currentUserCanRemoveContributors()"
                        @remove-friend-from-suggested="(id) => removeFriendFromSuggested(id)"
                    />
                </li>
            </ul>

            <div class="divider"></div>

            <h2><span v-if="bookshelfMembers?.length">{{ bookshelfMembers.length }}</span> Members</h2>

            <ul class="collaborators-list">
                <li v-for="friend in bookshelfMembers" :key="friend?.id">
                    <BookshelfCollaborator role="contributor"
                        :friend="friend" 
                        :bookshelf-id="route.params.bookshelf"
                        :current-user-is-admin="currentUserCanRemoveContributors()"
                        @remove-friend-from-suggested="(id) => removeFriendFromSuggested(id)"
                    />
                </li>
            </ul>
        </div>

        <div class="divider"></div>

        <!-- If user has friends render this shit -->
        <div v-if="dataLoaded">
            <h3 class="collaborator-tab active text-center">
                Add friends to your bookshelf
            </h3>

            <ul class="collaborators-list" v-if="currentView === 'close-friends'">
                <SearchUsers :friends-only="true"
                    class="mb-5"
                    @search-friends-result="(friendData) => searchFriendsResult = friendData"
                />
                
                <div v-if="searchFriendsResult?.length">
                    <li v-for="friend in searchFriendsResult" :key="friend?.id">
                        <BookshelfCollaborator :friend="friend"/>
                    </li>
                </div>

                <div v-else-if="suggestedFriendsForShelf?.length">
                    <li v-for="friend in suggestedFriendsForShelf" :key="friend?.id">
                        <BookshelfCollaborator :friend="friend" 
                        :bookshelf-id="route.params.bookshelf"
                        @remove-friend-from-suggested="(id) => removeFriendFromSuggested(id)"
                        />
                    </li>
                </div>
            </ul>
            <!-- <PaginationControls @increment="(startEndInts) => setPagination(startEndInts)"/> -->
        </div>

        <!-- What to do if users don't have friends, direct them to either a link generator for sign up that sends a friend request auto  -->
        <div v-if="dataLoaded && !suggestedFriendsForShelf?.length">
            <!-- Only render one of these depending on whether or not users have pending friend requests or not-->
            <div class="collaborator-cta" v-if="pendingFriendCount">
                <h2 class="add-friends-heading-text">You haven't connected with your friends on (name of our app) yet.</h2>
                
                <p class="add-friends-description-text">Invite them to join <a href="" class="underline text-indigo-500">here.</a> <br/></p>
            </div>

            <div class="collaborator-cta" v-else>
                <h2 class="add-friends-heading-text">You haven't connected with your friends on (name of our app) yet.</h2>
                
                <p class="add-friends-description-text">Accept your requests to add a friend to this bookshelf</p>

                <a href="" class="underline text-indigo-500">
                    Accept friend requests
                </a>
            </div>
        </div>

        <div v-if="!dataLoaded" class="loading">Loading <IconLoading /></div>
    </div>
</template>

<script setup>
import BookshelfCollaborator from './BookshelfCollaborator.vue';
import SearchUsers from '../social/SearchFriends.vue';
import { ref, onMounted, computed } from 'vue';
import { db } from '../../../services/db';
import { urls } from '../../../services/urls';
import { useRoute } from 'vue-router';
import IconInfo from '../../svg/icon-info.vue';
import IconLoading from '../../svg/icon-loading.vue';

const props = defineProps({
    bookshelf: {
        type: Object,
        required: true,
    },
});


const route = useRoute();
const suggestedFriendsForShelf = ref([]);
const pendingFriendCount = ref(0);
const bookshelfContributors = ref([]);
const bookshelfMembers = ref([]);
const bookshelfOwner = ref(null);
const currentView = ref('close-friends');
const searchFriendsResult = ref([]);
const dataLoaded = ref(false);
let hiddenFriends = [];

const modals = ref({
    showInfoModal: false,
});

// Need to add this to our backend somehow for paginating through suggested friends.
const currentPaginationGroupEnd = ref(0);
const currentPaginationGroupStart = ref(5);

// pagination is handled on backend for now.
const setPagination = (startEndInts) => {
    currentPaginationGroupStart.value = startEndInts[0];
    currentPaginationGroupEnd.value = startEndInts[1];
}

async function loadSuggestedFriends(){
    await db.get(urls.user.getFriends(route.params.user), `includes_pending=true&bookshelf_id=${route.params.bookshelf}`).then((res) => {
        suggestedFriendsForShelf.value = res.friends;
        pendingFriendCount.value = res.pendingCount;
    });
};

async function loadShelfContributors(){
    await db.get(urls.rtc.getBookshelfContributors(route.params.bookshelf)).then((res) => {
        bookshelfOwner.value = res.contributors.find((contributor) => contributor.role === 'owner');

        bookshelfContributors.value = res.contributors.filter((contributor) => contributor.role !== 'owner');
    })
}

async function loadShelfMembers(){
    await db.get(urls.rtc.getBookshelfMembers(route.params.bookshelf)).then((res) => {
        bookshelfMembers.value = res.members;
    })
}

// Add it to array and hide.
function removeFriendFromSuggested(id){
    hiddenFriends.push(id);
    sethiddenUserFromShelfInLS();
};

function sethiddenUserFromShelfInLS(){
    localStorage.setItem(`${route.params.bookshelf}-${route.params.user}-hidden-friends`, hiddenFriends);
};

// used for admin permissions on bookshelves.
const currentUserCanRemoveContributors = () => {
    if(route.params.user === props.bookshelf.created_by){
        return true;
    }
}


onMounted(async () => {
    hiddenFriends = localStorage.getItem(`${route.params.bookshelf}-${route.params.user}-hidden-friends`);
    const suggestedFriendsPromise = await loadSuggestedFriends()
    const loadShelfContributorsPromise = await loadShelfContributors();
    const loadShelfMembersPromise = await loadShelfMembers();

    // wait for all data to load then set dataLoaded to true.
    Promise.all([loadShelfContributorsPromise, suggestedFriendsPromise, loadShelfMembersPromise]).then(() => {
        dataLoaded.value = true;
    })
});
</script>
<style scoped>
.bookshelf-note {
    background-color: var(--stone-100);
    font-size: var(--font-sm);
    color: var(--stone-600);
    margin-bottom: var(--margin-md);
    margin-left: auto;
    margin-left: right;
    text-align: start;
    border-radius: var(--radius-sm);
    padding: var(--padding-sm);
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

.add-friends-heading-text {
    font-size: var(--font-2xl);
    color: var(---stone-700);
}

.add-friends-description-text {
    padding-top: var(--padding-sm);
    font-size: var(--font-lg);
    color: var(---stone-500);
}

.loading {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 40px;
    column-gap: 12px;
}
</style>