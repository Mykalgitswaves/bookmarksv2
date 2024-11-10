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
        <div class="pt-5 pb-5 flex items-center">
            <h4 class="text-stone-500 text-lg italic">{{ invites.length ? invites.length + 1 : 0 }} Notifications </h4>

            <CloseButton class="ml-auto" @close="notificationSidebar.close()"/>
        </div>

        <div v-if="loaded">
            <h3 class="fancy text-stone-600 text-xl">Bookclubs</h3>
            <!-- IF YOU HAVE INVITES -->
            <div v-if="invites.length">
                <div v-for="invite in invites" :key="invite.id" class="notifications bookclub">
                <!-- 
                invites are going to look like:
                 [[ {{ username }} invited you to their bookclub: {{ clubname }} ---- {accept} {decline} ]] 
                -->
                </div>
            </div>

            <!-- NO INVITES CHAT -->
            <div v-else class="fancy text-base text-stone-500">
                you don't have any outstanding invites
            </div>
        </div>

        <div v-else class="gradient fancy text-center text-lg loading-box">
            <h3>Loading activity</h3>
        </div>
        <!-- TODO: Add other notifications once bookclubs are done -->
    </dialog> 
</template>
<script setup>
import { db } from '../../../services/db';
import { urls } from '../../../services/urls';
import { onBeforeUnmount, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import IconBellNotificationActive from '../../svg/icon-bell-notification-active.vue';
import IconBellNotificationInert from '../../svg/icon-bell-notification-inert.vue';
import CloseButton from '../partials/CloseButton.vue'

/**
 * @constants
 */

const route = useRoute();
const notificationSidebar = ref(null);
const notificationsButton = ref(null);
const loaded = ref(false);
const isOpen = ref(false);

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

let invites = [];

// Chat SC suffix is short for successcallback, im using slang chat.
const loadInvitesSC = (res) => (invites = res.invites)
const loadInvitesEC = (err) => console.warn(err);


function load() {
    const invitesPromise = db.get(urls.bookclubs.getInvitesForUser(route.params.user), null, false, loadInvitesSC, loadInvitesEC);
    Promise.resolve([invitesPromise]).then(() => {
        loaded.value = true;
    });
}
/**
 * @FIRE
 */

load();

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
    background-color: var(--stone-50);
}

.sidebar-menu::backdrop {
  display:none
}

.notification {
    padding: 8px;
    display: flex;
    justify-content: space-around;
    column-gap: 8px;
}
</style>