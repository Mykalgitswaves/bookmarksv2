<template>
    <button 
        ref="notificationsButton"
        class="btn  btn-tiny btn-icon h-40 transition" 
        :class="{
            'btn-submit': hasSomeClubNotifications,
            'btn-specter': !hasSomeClubNotifications,
        }"
        type="button"
        @click="showOrHideSideBar"
    >
        <IconBellNotificationActive v-if="hasSomeClubNotifications" />

        <IconBellNotificationInert v-else/>
    </button>
    
    <dialog ref="notificationSidebar" class="sidebar-menu">
        <CloseButton class="absolute r-20" @close="notificationSidebar.close()"/>

        <div class="grid-two-cols pb-5" style="column-gap: 5px; width: 80%;">
            <button type="button" 
                class="btn btn-tiny btn-ghost btn-toolbar fancy text-sm" 
                :class="{'active': viewingClubNotifications}" 
                @click="viewingClubNotifications = true"
            >
                Club
            </button>
            
            <button type="button" 
                class="btn btn-tiny btn-ghost btn-toolbar fancy text-sm" 
                :class="{'active': !viewingClubNotifications}" 
                @click="viewingClubNotifications = false"
            >
                Invites
            </button>
        </div>

        <div v-if="viewingClubNotifications">
            <AsyncComponent 
                :promise-factory="clubNotificationsFactory" 
                :subscribed-to="clubNotificationsRequestSubscriptionId"
            >
                <template #resolved>    
                    <div v-if="Object.values(clubNotifications).some((club) => club.notifications.length)">
                        <div class="filters">
                            <label 
                                class="filter-option" 
                                :class="{'active': !!filterOptions.peerPressure}" 
                                :for="ClubNotification.types.peerPressure" 
                            >
                                <input
                                    type="checkbox" 
                                    v-model="filterOptions.peerPressure"
                                    :id="ClubNotification.types.peerPressure"
                                >

                                <span class="text-stone-500 text-xs">
                                    {{ ClubNotification.labels[ClubNotification.types.peerPressure] }}
                                </span>
                            </label>

                            <label 
                                class="filter-option" 
                                :class="{'active': !!filterOptions.finishedReading}" 
                                :for="ClubNotification.types.finishedReading" 
                            >
                                <input
                                    type="checkbox"
                                    v-model="filterOptions.finishedReading"
                                    :id="ClubNotification.types.finishedReading"
                                >
                                <span class="text-stone-500 text-xs">
                                    {{ ClubNotification.labels[ClubNotification.types.finishedReading] }}
                                </span>
                            </label>
                        </div>
                        
                        <!-- CLUBS CLUBS CLUBS -->
                         <!-- This is a series of club notifications -->
                        <div v-for="club in computedClubNotifications" :key="club.id" class="club">
                            <!-- Looking at an individual club in a loop of clubs -->
                            <h4 class="text-stone-700 text-xl fancy">{{ club.clubName }}</h4>

                            <div class="notification-categories-scroll-container">
                                <!-- FINISHED READING! -->
                                <div class="notifications-category" 
                                    v-if="club.finishedReadingNotifications.length === 1 && !filterOptions.finishedReading"
                                >
                                    <div class="club-notification" v-if="!club.finishedReadingNotifications[0].dismissed">
                                        <p class="club-notification-date text-xs text-stone-600">
                                            {{ dates.timeAgoFromNow(club.finishedReadingNotifications[0].created_date) }}
                                        </p>
                                        
                                        <h5 class="text-stone-600 text-sm">
                                            <span class="bold italic text-indigo-400">
                                                {{ club.finishedReadingNotifications[0].sent_by_user_username }}</span> just finished reading: <br/>
                                            <span class="bold italic">{{ club.currentlyReadingBookTitle  }}</span>
                                        </h5>

                                        <div class="club-notification-button-group">
                                            <button type="button" 
                                                class="btn btn-submit btn-tiny text-xs fancy"
                                                @click="dismissNotification(club.finishedReadingNotifications[0], null)"
                                            >Dismiss</button>
                                            
                                            <!-- TODO: Add this in. v-if="club.finishedReadingNotifications[0].posted_review"  -->
                                            <button
                                                type="button" 
                                                class="btn btn-submit btn-tiny text-xs fancy"
                                                @click="() => {
                                                        dismissNotification(club.finishedReadingNotifications[0], null);
                                                        router.push(urls.concatQueryParams(
                                                            navRoutes.toBookClubFeed(route.params.user, club.id),
                                                            {'update': club.finishedReadingNotifications[0].id}, 
                                                            true,
                                                        ))
                                                }"    
                                            >Go to club</button>
                                        </div>
                                    </div>
                                </div>

                                <div class="notifications-category" 
                                    v-if="club.finishedReadingNotifications.length > 1 && !filterOptions.finishedReading"
                                >
                                    <div class="club-notification" v-if="!club.finishedReadingNotifications[0].dismissed">
                                        <p class="club-notification-date text-xs text-stone-600">
                                            {{ dates.timeAgoFromNow(club.finishedReadingNotifications[0].created_date) }}
                                        </p>
                                        
                                        <h5 class="text-stone-600 text-sm">
                                            <span class="bold italic text-indigo-400">
                                                {{ club.finishedReadingNotifications[0].sent_by_user_username }}</span> and
                                            <span class="bold italic text-indigo-400">
                                                {{ club.finishedReadingNotifications.length - 1 }}
                                            </span> others have finished reading: <br/>
                                            <span class="bold italic">{{ club.currentlyReadingBookTitle  }}</span>
                                        </h5>

                                        <div class="club-notification-button-group">
                                            <button type="button" 
                                                class="btn btn-submit btn-tiny text-xs fancy"
                                                @click="dismissNotification(null, club.finishedReadingNotifications)"
                                            >Dismiss</button>
                                            
                                            <!-- TODO: Add this in. v-if="club.finishedReadingNotifications[0].posted_review"  -->
                                            <button
                                                type="button" 
                                                class="btn btn-submit btn-tiny text-xs fancy"
                                                @click="() => {
                                                        dismissNotification(null, club.finishedReadingNotifications);
                                                        router.push(urls.concatQueryParams(
                                                            navRoutes.toBookClubFeed(route.params.user, club.id),
                                                            {'update': club.finishedReadingNotifications[0].id}, 
                                                            true,
                                                        ))
                                                }"    
                                            >Go to club</button>
                                        </div>
                                    </div>
                                </div>

                                <!-- If you have finished reading notifications, but you have filtered them out -->
                                <div v-if="filterOptions.finishedReading" class="notifications-category filtered">
                                    <h5 class="text-stone-400 italic text-sm mt-2"> 
                                        🪄 Finished reading notifications filtered...✨
                                    </h5>
                                </div>




                                <div class="notifications-category" v-if="club.peerPressureNotifications?.length && !filterOptions.peerPressure">
                                    <div v-if="club.peerPressureNotifications?.length  === 1">
                                        <div class="club-notification" 
                                            v-if="!club.peerPressureNotifications[0].dismissed"
                                        >
                                            <p class="club-notification-date text-xs text-stone-600">{{ dates.timeAgoFromNow(club.peerPressureNotifications[0].created_date) }}</p>
                                            
                                            <h5 class="text-stone-600 text-sm">
                                                <span class="bold italic text-indigo-400">{{ club.peerPressureNotifications[0].sent_by_user_username }}</span> wants to hear your thoughts
                                                on: <br>
                                                <span class="bold italic">{{ club.currentlyReadingBookTitle  }}</span>
                                            </h5>

                                            <div class="club-notification-button-group">
                                                <button type="button" 
                                                    class="btn btn-submit btn-tiny text-xs fancy"
                                                    @click="dismissNotification(club.peerPressureNotifications[0], null)"
                                                >Dismiss</button>
                                                
                                                <button type="button" 
                                                    class="btn btn-submit btn-tiny text-xs fancy"
                                                    @click="() => {
                                                            dismissNotification(club.peerPressureNotifications[0], null);
                                                            router.push(urls.concatQueryParams(
                                                                navRoutes.toBookClubFeed(route.params.user, club.id),
                                                                {'make-update': true}, 
                                                                true,
                                                            )
                                                        )
                                                    }"    
                                                >Write an update</button>
                                            </div>
                                        </div>

                                        <h4 v-else class="fancy text-sm text-stone-600">🪄 Dismissed! 🪄</h4>
                                    </div>

                                    <!-- You have multiple notifications for the same club -->
                                    <div v-if="club.peerPressureNotifications.length > 1">
                                        <div class="club-notification" v-if="!club.peerPressureNotifications[0].dismissed">
                                            <p class="club-notification-date text-xs text-stone-600">{{ dates.timeAgoFromNow(club.peerPressureNotifications[0].created_date) }}</p>
                                            
                                            <h5 class="text-stone-600 text-sm">
                                                <span class="bold italic text-indigo-400">{{ club.peerPressureNotifications[0].sent_by_user_username }}</span> and 
                                                <span class="bold italic text-indigo-400">{{ club.peerPressureNotifications.length - 1}} </span>
                                                others want to hear your thoughts on: <span class="bold italic">{{ club.currentlyReadingBookTitle  }}</span>
                                            </h5>

                                            <div class="club-notification-button-group" v-if="!club.peerPressureNotifications[0].dismissed">
                                                <button 
                                                    type="button" 
                                                    class="btn btn-tiny btn-submit text-xs fancy"
                                                    @click="dismissNotification(
                                                        null, 
                                                        club.peerPressureNotifications
                                                    )"
                                                >Dismiss 🪄</button>
                                                
                                                <button type="button" 
                                                    class="btn btn-tiny btn-submit text-xs fancy" 
                                                    @click="() => {
                                                        dismissNotification(
                                                            null, 
                                                            club.peerPressureNotifications
                                                        );
                                                        router.push(
                                                            urls.concatQueryParams(
                                                                navRoutes.toBookClubFeed(route.params.user, club.id),
                                                                {'make-update': true}, 
                                                                true,
                                                            )
                                                        );
                                                    }"
                                                >
                                                    Write an update
                                                </button>
                                            </div>

                                            <h4 v-else class="fancy text-sm text-stone-600">🪄 Dismissed! 🪄</h4>
                                        </div>
                                    </div>
                                </div>

                                <div v-else class="notifications-category filtered">
                                    <h5 class="text-stone-400 italic text-sm mt-2">🪄 Peer pressure Notifications filtered...✨</h5>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div v-else>
                        <h4 class="text-stone-600 fancy ml-5">
                            No club notifications
                        </h4>
                    </div>
                </template>

                <template #loading>
                    <div class="gradient fancy text-center text-lg loading-box mt-5">
                        <h3>Loading Notifications</h3>
                    </div>
                </template>
            </AsyncComponent>
        </div>

        <div v-else>
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
                        <div v-if="friendRequestStatus[request.from_user.id] === Requests.STATUSES.anonymous_user_friend_requested" 
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
                                            friendRequestStatus[request.from_user.id] = Requests.STATUSES.friends;
                                            console.log('yall are friends now')
                                        }
                                    )"
                                >
                                    Accept
                                </button>

                                <button 
                                    type="button" 
                                    class="btn btn-tiny btn-red text-sm"
                                    @click="declineFriendRequest(request.from_user.id, () => {
                                        friendRequestStatus[request.from_user.id] = Requests.STATUSES.declined;
                                        console.log('Why yall hate each other bro')
                                    })"
                                >   
                                    Decline
                                </button>
                            </div>
                        </div>

                        <!-- If you accepted a friend request. IE. friends -->
                        <div v-else-if="friendRequestStatus[request.from_user.id] === Requests.STATUSES.friends"
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
                        <div v-else-if="friendRequestStatus[request.from_user.id] === Requests.STATUSES.declined"
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
        </div>
    </dialog> 
</template>
<script setup>
import { db } from '../../../services/db';
import { urls, navRoutes } from '../../../services/urls';
import { acceptFriendRequest, declineFriendRequest } from './notificationService.js';
import { acceptInviteToBookClub, declineInviteToBookClub } from '../bookclubs/bookClubService';
import { Requests } from '../../../models/friend-requests.js';
import { PubSub } from '../../../services/pubsub.js';
import { onBeforeUnmount, ref, watch, reactive, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { dates } from '../../../services/dates';
import IconBellNotificationActive from '../../svg/icon-bell-notification-active.vue';
import IconBellNotificationInert from '../../svg/icon-bell-notification-inert.vue';
import CloseButton from '../partials/CloseButton.vue'
import AsyncComponent from '../partials/AsyncComponent.vue';
import { ClubNotification } from '../bookclubs/club/notifications/models.js';

/**
 * @constants
 */

const { timeAgoFromNow } = dates;
const route = useRoute();
const { user } = route.params;
const router = useRouter();
const notificationSidebar = ref(null);
const notificationsButton = ref(null);
const isOpen = ref(false);

const dismissedNotifications = ref({});
// Needed to know whether to say you accepted or declined a request.
const friendRequestStatus = ref({});
// Look in AsyncComponent.vue for why im doing.
const inviteRequestSubscriptionId = 'notifications-get-invites';
const friendRequestSubscriptionId = 'notifications-get-friends';
const clubNotificationsRequestSubscriptionId = 'notifications-get-club-notifications';

let invites = [];
let friendRequests = [];

const hasSomeClubNotifications = computed(() => {
    return !!Object.values(clubNotifications).some((club) => club.notifications.length)
});

const clubNotifications = reactive({});
const viewingClubNotifications = ref(true);

// Used for filtering out notification types dude
const filterOptions = reactive({
    peerPressure: false,
    finishedReading: false,
});

// Filter out notifications by type that might also be actively being filtered?
// We want this to be a function so we can have multiple lists of notification types for a single club section.
// If the filterOptions is true, that means we WANT to filter out a notification from our list - not show it!
// Computed function, so that it will rerender whenever filterOptions ref changes!
const computedClubNotifications = computed(() => {
    console.log('recomputing club notifications');
    return Object.entries(clubNotifications).map(([key, club]) => (
        {   
            id: key,
            clubName: club.book_club_name,
            currentlyReadingBookTitle: club.currently_reading_book_title,
            peerPressureNotifications: club.notifications.filter(
                (notification) => (
                    notification.notification_type === ClubNotification.types.peerPressure
                )
            ),
            finishedReadingNotifications: club.notifications.filter(
                (notification) => (
                    notification.notification_type === ClubNotification.types.finishedReading
                )
            ) 
        }
    ))
})


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
        PubSub.publish(clubNotificationsRequestSubscriptionId);
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
            dismissedNotifications.value[invite.id] = false;
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
            friendRequestStatus.value[request.from_user.id] = Requests.STATUSES.anonymous_user_friend_requested;
        });
    }, 
    (err) => {
        console.error(err)
    }
);

const clubNotificationsFactory = () => db.get(urls.bookclubs.getClubNotificationsForUser(user), null, false, 
    (res) => {
        Object.assign(clubNotifications, res.notifications);
    }, (err) => {
        console.log(err);
    }
);

async function dismissNotification(notification, notificationArray) {
    if (notification && !notificationArray) {
        db.put(urls.bookclubs.dismissClubNotification(notification.id), null, false, () => {
            notification.dismissed = true;
        });
    } else {
        // Make a ton of different requests.
        notificationArray.map(
            (notification) => (
                db.put(urls.bookclubs.dismissClubNotification(notification.id), 
                    null, 
                    false, 
                    () => {
                        notification.dismissed = true;
                    }
                )
            )
        );
    }
}

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
    display: inline-block;
    padding: 8px 16px;
}

.notification[declined] {
    background-color: var(--red-50);
    display: inline-block;
    padding: 8px 16px;
}

.r-20 {
    right: 20px;
}


/* Notification types */
@starting-style {
    .club-notification {
        opacity: 0;
        height: 0;
    }
}

.club-notification {
    position: relative;
    border-radius: 4px;
    margin-top: 20px;
    margin-bottom: 4px;
    display: grid;
    grid-template-columns: 1fr auto;
    column-gap: 8px;
    align-items: center;
    justify-content: space-between;

    & .club-notification-date {
        position: absolute;
        bottom: -16px; 
        left: 0;
        font-style: italic;
    }
}

.notification-categories-scroll-container {
    overflow-y: scroll;
    max-height: 240px;
}

@starting-style {
    .notifications-category {
        opacity: 0; 
    }
}

.notifications-category {
    border-bottom: 1px solid var(--stone-200);
    padding-bottom: 28px;
    margin-bottom: 14px;
    transition: all ease 250ms; 

    &.filtered {
        padding-bottom: 14px;
    }
}

.club-notification-button-group {
    display: flex;
    flex-direction: column;
    row-gap: 4px;
    @media screen and (min-width: 768px) {
        column-gap: 4px;
        flex-direction: row;
    }

}

.dismissed {
    display: none;
}

.filters {
    display: flex;
    column-gap: 14px;
    margin-bottom: 8px;
}

.filter-option {
    display: flex;
    align-items: start;
    line-height: .9;
    column-gap: 8px;
    padding: 4px 8px;
    border: 1px solid var(--stone-200);
    border-radius: 4px;
    font-family: var(--fancy-script);

    input[type=checkbox] {
        appearance: none;
        display: none;
    }

    &.active {
        border-color: var(--indigo-300);
        background-color: var(--indigo-50);
    }
}

.club {
    margin-top: 20px;
}
</style>