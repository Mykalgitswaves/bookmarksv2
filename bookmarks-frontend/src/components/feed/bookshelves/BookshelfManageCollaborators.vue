<template>
    <!-- Toolbar -->
    <div class="toolbar my-5">
        <button type="button"
            class="btn btn-tiny btn-toolbar"
            :class="{'active': isViewingContributors}"
            @click="isViewingContributors = true"
        >
            Manage contributors
        </button>
        <button type="button"
            class="btn btn-tiny btn-toolbar"
            :class="{'active': !isViewingContributors}"
            @click="isViewingContributors = false"
        >
            Add contributors
        </button>
    </div>

    <div class="mt-5">
        <section v-if="isViewingContributors">
            <button type="button" 
                class="btn flex gap-2 mb-2 pl-0" 
                @click="modals.showInfoModal = !modals.showInfoModal"
            >
                <IconInfo />

                learn more about contributors

                <IconChevron :style="{transform: modals.showInfoModal ? 'rotate(180deg)' : ''}" class="ml-2"/>
            </button>

            <Transition name="content" tag="div">
                <div role="note" 
                    id="collaborator-note" 
                    v-if="!modals.showInfoModal" 
                    @click="modals.showInfoModal = !modals.showInfoModal">
                    <p class="bookshelf-note">
                        Contributors have the ability to add, remove and reorder books.
                        You can manage your contributors here. bookshelves can have a maximum limit of 5 contributors.
                        Members are able to view books but cannot edit bookshelves.
                    </p>
                </div>
            </Transition>

            <TransitionGroup tag="div" name="content">
                <div v-if="dataLoaded">
                    <h2 class="section-heading">Owner</h2>

                    <BookshelfCollaborator 
                        v-if="bookshelfOwner"
                        :role="bookshelfOwner?.role"
                        :friend="bookshelfOwner" 
                        :current-user-is-admin="currentUserCanRemoveContributors()"
                    />
                </div>

                <!-- All contributors of shelf. -->
                <div v-if="bookshelfContributors?.length">
                    <div class="divider"></div>
                    
                    <h2 class="section-heading">
                        <span v-if="bookshelfContributors?.length" 
                            class="accent"
                        >{{ bookshelfContributors.length }}</span> Contributors
                    </h2>

                    <ul class="collaborators-list">
                        <li v-for="(friend, index) in bookshelfContributors" :key="friend.id">
                            <BookshelfCollaborator role="contributor"
                                :friend="friend" 
                                :bookshelf-id="route.params.bookshelf"
                                :current-user-is-admin="currentUserCanRemoveContributors()"
                                @removed-contributor="(contributor_id) => removeFromList('contributor', contributor_id)"
                            />
                        </li>
                    </ul>
                </div>

                <!-- All members of a shelf -->
                <div v-if="bookshelfMembers?.length">
                    <div class="divider"></div>

                    <h2 class="section-heading">
                        <span v-if="bookshelfMembers?.length" 
                            class="accent"
                        >{{ bookshelfMembers.length }}</span> Members
                    </h2>

                    <ul class="collaborators-list">
                        <li v-for="(friend, index) in bookshelfMembers" :key="friend?.id">
                            <BookshelfCollaborator role="contributor"
                                :friend="friend" 
                                :bookshelf-id="route.params.bookshelf"
                                :current-user-is-admin="currentUserCanRemoveContributors()"
                                @removed-member="(member_id) => removeFromList('member', member_id)"
                            />
                        </li>
                    </ul>
                </div>
            </TransitionGroup>
        </section>

        <section v-else>
            <!-- If user has friends render this shit -->
            <div v-if="dataLoaded">
                <ul class="collaborators-list">
                    <div class="mx-auto">
                        <SearchUsers v-if="suggestedFriendsForShelf?.length" 
                            :friends-only="true"
                            class="mb-5"
                            :bookshelf-id="route.params.bookshelf"
                            label-above="Friends added to this shelf as members or contributors won't appear in search results"
                            @search-friends-result="(friendData) => searchFriendsResult = friendData"
                        />
                    </div>
                    
                    <div v-if="searchFriendsResult?.length">
                        <li v-for="friend in searchFriendsResult" :key="friend?.id">
                            <BookshelfCollaborator :friend="friend"
                                @added-contributor="(user_id) => addFriendToList('contributor', user_id)"
                                @added-member="(user_id) => addFriendToList('member', user_id)"
                            />
                        </li>
                    </div>

                    <div v-else-if="suggestedFriendsForShelf?.length">
                        <li v-for="friend in suggestedFriendsForShelf" :key="friend?.id">
                            <BookshelfCollaborator :friend="friend" 
                                :bookshelf-id="route.params.bookshelf"
                                :is-suggested="true"
                                @added-contributor="(user_id) => addFriendToList('contributor', user_id)"
                                @added-member="(user_id) => addFriendToList('member', user_id)"
                            />
                            <!-- Figure out what we are doing with remove friend from suggested. -->
                            <!-- @remove-friend-from-suggested="(id) => removeFriendFromSuggested(id)" -->
                        </li>
                    </div>
                </ul>
                <!-- <PaginationControls @increment="(startEndInts) => setPagination(startEndInts)"/> -->
            </div>

            <!-- What to do if users don't have friends, direct them to either a link generator for sign up that sends a friend request auto  -->
            <div v-if="dataLoaded && !suggestedFriendsForShelf?.length">
                <!-- Only render one of these depending on whether or not users have pending friend requests or not-->
                <div class="collaborator-cta" v-if="!pendingFriendCount">
                    <h2 class="add-friends-heading-text">Need more friends? <span>(dont worry we do too 🫥)</span></h2>
                    
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
        </section>

        <div v-if="!dataLoaded" class="mx-auto flex gap-2 items-center">Loading <IconLoading class="loading-spinner"/></div>
    </div>
</template>

<script setup>
import BookshelfCollaborator from './BookshelfCollaborator.vue';
import SearchUsers from '../social/SearchFriends.vue';
import { ref, onMounted, computed, toRaw } from 'vue';
import { db } from '../../../services/db';
import { urls } from '../../../services/urls';
import { useRoute } from 'vue-router';
import IconInfo from '../../svg/icon-info.vue';
import IconLoading from '../../svg/icon-loading.vue';
import IconChevron from '../../svg/icon-chevron.vue';

const props = defineProps({
    bookshelf: {
        type: Object,
        required: true,
    },
});
const emit = defineEmits(['added-friend-as-contributor', 'removed-friend-as-contributor']);
const route = useRoute();
const suggestedFriendsForShelf = ref([]);
const pendingFriendCount = ref(0);
const bookshelfContributors = ref([]);
const bookshelfMembers = ref([]);
const bookshelfOwner = ref(null);
const searchFriendsResult = ref([]);
const dataLoaded = ref(false);
const isViewingContributors = ref(false);
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
        console.log(res)
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

function removeFromList(listName, user_id){
    if(listName === 'contributor'){
        bookshelfContributors.value = bookshelfContributors.value.filter((contributor) => contributor.id !== user_id);
    } else if(listName === 'member'){
        bookshelfMembers.value = bookshelfMembers.value.filter((member) => member.id !== user_id);
    }
    emit('removed-friend-as-contributor');
}

function addFriendToList(listName, user_id){
    console.log(listName, user_id)
    let friend = suggestedFriendsForShelf.value.find((user) => user.id === user_id);
    
    if (friend) {
        friend = toRaw(friend)
    } else {
        return;
    }

    if (listName === 'contributor' && friend) {
        friend.role = 'contributor';
        bookshelfContributors.value.push(friend);
    } else if(listName === 'member' && friend){
        friend.role = 'member';
        bookshelfMembers.value.push(friend);
    }
    
    // Remove from shelf.
    suggestedFriendsForShelf.value = suggestedFriendsForShelf.value.filter((user) => user.id !== user_id);
    emit('added-friend-as-contributor');
}

onMounted(async () => {
    hiddenFriends = localStorage.getItem(`${route.params.bookshelf}-${route.params.user}-hidden-friends`);
    const suggestedFriendsPromise = await loadSuggestedFriends()
    const loadShelfContributorsPromise = await loadShelfContributors();
    const loadShelfMembersPromise = await loadShelfMembers();

    // wait for all data to load then set dataLoaded to true.
    Promise.all([loadShelfContributorsPromise, suggestedFriendsPromise, loadShelfMembersPromise]).then(() => {
        dataLoaded.value = true;
    });
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
    margin-top: calc(2 * var(--margin-md));
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

.collaborator-cta {
    text-align: center;
}

.add-friends-heading-text {
    color: var(--stone-700);
    font-size: var(--font-2xl);
    font-weight: 500;
}

.add-friends-description-text {
    padding-top: 2px;
    font-size: var(--font-lg);
    color: var(--stone-500);
}

.loading-spinner {
    animation: spin 1s infinite linear;
}

@keyframes spin {
    from {
        transform: rotate(0deg);
    } to {
        transform: rotate(360deg);
    }
}
</style>