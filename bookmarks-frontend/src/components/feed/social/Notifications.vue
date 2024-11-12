<template>
    <button 
        ref="notificationsButton"
        class="btn btn-ghost btn-tiny btn-icon h-40 transition" 
        type="button"
        @click="showOrHideSideBar"
    >
        <IconBellNotificationActive v-if="notifications?.length" />

        <IconBellNotificationInert v-else/>
    </button>
    
    <dialog ref="notificationSidebar" class="sidebar-menu">
        <div class="pt-5 pb-5">
            <CloseButton class="ml-auto" @close="notificationSidebar.close()"/>
        </div>

        <!-- BookClubInvites -->
        <AsyncComponent :promise-factory="invitesPromiseFactory" :subscribed-to="inviteRequestSubscriptionId">
            <template #resolved>
                <h3 class="fancy text-stone-600 text-xl">Bookclub invites</h3>
                <!-- IF YOU HAVE INVITES -->

                <div
                    v-for="invite in invites" 
                    :key="invite.id" 
                >
                    <div v-if="!dismissedNotifications[invite.invite_id]" class="notification">
                        <p class="text-sm text-stone-500 text-start">{{ timeAgoFromNow(invite.datetime_invited) }}</p>

                        <p class="text-stone-500 text-sm">
                            <!-- TODO: maybe add in a link to whoever invited you to the club. -->
                            <i>{{ invite.book_club_owner_name }}</i> invited you to: <br/>
                            <span class="text-stone-600 fancy bold">{{ invite.book_club_name }}</span>
                        </p>

                        <div class="flex gap-2 ml-auto">
                            <button 
                                type="button" 
                                class="btn btn-tiny btn-submit text-sm"
                                @click="acceptInviteToBookClub(invite.invite_id, () => { 
                                        dismissedNotifications[invite.invite_id] = true; 
                                    }
                                )"
                            >
                                Accept
                            </button>

                            <button 
                                type="button" 
                                class="btn btn-tiny btn-red text-sm"
                                @click="declineInviteToBookClub(invite.invite_id, () => { 
                                        dismissedNotifications[invite.invite_id] = true; 
                                    }
                                )"
                            >   
                                Decline
                            </button>
                        </div>
                    </div>

                    <div v-else-if="dismissedNotifications[invite.invite_id]" 
                        class="notification" accepted
                    >
                        <p class="text-stone-700 fancy">Welcome to 
                            <span class="bold text-indigo-600">{{ invite.book_club_name }}</span>🎉
                        </p>
                    </div>
                </div>

                <!-- NO INVITES CHAT -->
                <div v-if="!invites.length" class="fancy text-sm text-stone-500 mt-5">
                    you don't have any outstanding invites
                </div>
            </template>

            <template #loading>
                <div class="gradient fancy text-center text-lg loading-box">
                    <h3>Loading invites</h3>
                </div>
            </template>
        </AsyncComponent>


        <!-- Friend requests -->
        <AsyncComponent :promise-factory="friendRequestsPromiseFactory" :subscribed-to="friendRequestSubscriptionId">
            <template #resolved>
                <h3 class="fancy text-stone-600 text-xl mt-5">Friend requests</h3>
                <!-- IF YOU HAVE INVITES -->

                <div
                    v-for="request in friendRequests"
                    :key="request.id" 
                >
                    <div v-if="friendRequestStatus[request.id] === Requests.STATUSES.anonymous_user_friend_requested" 
                        class="notification"
                        pending
                    >
                        <p class="text-sm text-stone-500">{{ timeAgoFromNow(request.created_date) }}</p>

                        <p class="text-stone-500 text-sm">
                            <i class="text-stone-700">
                                <RouterLink :to="navRoutes.toUserPage(user, request.from_user.id)">
                                    {{ request.from_user.username }}
                                </RouterLink>
                            </i> wants to be friends
                        </p>

                        <div class="flex gap-2 ml-auto">
                            <button 
                                type="button" 
                                class="btn btn-tiny btn-submit text-sm"
                                @click="acceptFriendRequest(request.from_user.id, () => { 
                                        friendRequestStatus[request.id] = Requests.STATUSES.friends;
                                    }
                                )"
                            >
                                Accept
                            </button>

                            <button 
                                type="button" 
                                class="btn btn-tiny btn-red text-sm"
                                @click="declineFriendRequest(request.from_user.id, () => {

                                    friendRequestStatus[request.id] = Requests.STATUSES.declined
                                })"
                            >   
                                Decline
                            </button>
                        </div>
                    </div>

                    <!-- If you accepted a friend request. IE. friends -->
                    <div v-else-if="friendRequestStatus[request.id] === Requests.STATUSES.friends"
                        class="notification" 
                        accepted
                    >
                        <p class="text-stone-700 fancy">You and 
                            <span class="text-indigo-600 bold">{{ request.from_user.username }}</span>
                            are now friends 🎉
                        </p>
                        <!-- DO WE WANT TO GIVE PEOPLE THE OPTION TO UNDO HERE? -->
                    </div>

                    <!-- If you declined a friend request. IE. not friends -->
                    <div v-else-if="friendRequestStatus[request.id] === Requests.STATUSES.declined"
                        class="notification" 
                        declined
                    >
                        Request declined 🤖
                    </div>
                </div>

                <!-- NO INVITES CHAT -->
                <div v-if="!friendRequests.length" class="fancy text-sm text-stone-500 mt-5">
                    you don't have any outstanding requests
                </div>
            </template>

            <template #loading>
                <div class="gradient fancy text-center text-lg loading-box mt-5">
                    <h3>Loading requests</h3>
                </div>
            </template>
        </AsyncComponent>
        <!-- TODO: Add other notifications once bookclubs are done -->
    </dialog> 
</template>
<script setup>
import { db } from '../../../services/db';
import { urls, navRoutes } from '../../../services/urls';
import { acceptFriendRequest, declineFriendRequest } from './notificationService.js';
import { acceptInviteToBookClub, declineInviteToBookClub } from '../bookclubs/bookClubService';
import { Requests } from '../../../models/friend-requests.js';
import { PubSub } from '../../../services/pubsub.js';
import { onBeforeUnmount, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { dates } from '../../../services/dates';
import IconBellNotificationActive from '../../svg/icon-bell-notification-active.vue';
import IconBellNotificationInert from '../../svg/icon-bell-notification-inert.vue';
import CloseButton from '../partials/CloseButton.vue'
import AsyncComponent from '../partials/AsyncComponent.vue';

/**
 * @constants
 */

const route = useRoute();
const notificationSidebar = ref(null);
const notificationsButton = ref(null);
const isOpen = ref(false);
const dismissedNotifications = ref({});
// Needed to know whether to say you accepted or declined a request.
const friendRequestStatus = ref({});
const { timeAgoFromNow } = dates;
const { user } = route.params;

// Look in AsyncComponent.vue for why im doing.
const inviteRequestSubscriptionId = 'notifications-get-invites';
const friendRequestSubscriptionId = 'notifications-get-friends';

let invites = [];
let friendRequests = [];

/**
 * @UI_functions
 */
function showOrHideSideBar() {
    if (notificationSidebar.value) {
        if (!notificationSidebar.value.open) { 
            notificationSidebar.value.showModal(); 
            isOpen.value = true; 
        } else {
            notificationSidebar.value.close();
            isOpen.value = false;
        } 
    }
}


function handleClickOutside(event){
    if (
        notificationSidebar.value 
        && notificationSidebar.value.open 
        && !(notificationSidebar.value.contains(event.target) || 
        notificationsButton.value.contains(event.target))
    ) {
        notificationSidebar.value.close();
        isOpen.value = false;

        PubSub.publish(inviteRequestSubscriptionId);
        PubSub.publish(friendRequestSubscriptionId);
    }
}

// Make a watcher for an event listener when someone clicks outside the dialog. 
watch(
    isOpen, 
    (newValue) => {
        if (newValue) {
            document.addEventListener('click', (event) => handleClickOutside(event));
            watch();
        }
    },
);

/**
 * @promises 
 */

const invitesPromiseFactory = () => db.get(urls.bookclubs.getInvitesForUser(user), null, false, 
    (res) => {
        invites = res.invites;

        res.invites.forEach((invite) => {
            acceptedInvites.value[invite.id] = false;
        });
    }, 
    (err) => {
        console.error(err);
    }
);

const friendRequestsPromiseFactory = () => db.get(urls.user.getUsersFriendRequests(user), null, false, 
    (res) => {
        friendRequests = res.data;

        res.data.forEach((request) => {
            friendRequestStatus.value[request.id] = Requests.STATUSES.anonymous_user_friend_requested;
        });
    }, 
    (err) => {
        console.error(err)
    }
);

onBeforeUnmount(() => {
    document.removeEventListener('click', handleClickOutside)
});
</script>
<style scoped>
.h-40 {
    height: 40px;
}

.transition {
    transition: all 250ms ease-in-out;
}

@starting-style {
    .sidebar-menu {
        opacity: 0;
        height: 0;
        right: -9999px;
    }
}

.sidebar-menu[open] {
    --mobile-sidebar-width: 70vw;
    @media screen and (min-width: 768px) {
        --mobile-sidebar-width: 700px;
    }

    transition-behavior: allow-discrete;
    transition: 300ms ease;
    width: var(--mobile-sidebar-width);
    min-width: 300px; /** For mobile */
    border: 1px solid var(--stone-200);
    border-radius: var(--radius-md);
    margin: var(--margin-md);
    margin-left: auto;
    margin-top: 60px;
    padding: 24px;
    padding-top: 0;
    background-color: var(--surface-primary);
}

.sidebar-menu::backdrop {
  display:none
}

@starting-style {
    .notification {
        opacity: 0;
    }
}

.notification {
    padding: 8px;
    padding-left: 0;
    display: grid;
    grid-template-columns: 80px auto auto;
    align-items: center;
    column-gap: 8px;
    width: 100%;
    transition: var(--transition-medium);
    margin-top: 10px;
}

.notification[accepted] {
    background-color: var(--green-50);
}
</style>