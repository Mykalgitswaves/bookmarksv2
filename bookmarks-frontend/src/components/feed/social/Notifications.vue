<template>
    <button ref="mobileMenuButton"
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

        <div>
            <!-- Collapsible notification sliders -->
            
        </div>
    </dialog> 
</template>
<script setup>
import { db } from '../../../services/db';
import { urls } from '../../../services/urls';
import { computed, ref } from 'vue';
import { useRoute } from 'vue-router';
import IconBellNotificationActive from '../../svg/icon-bell-notification-active.vue';
import IconBellNotificationInert from '../../svg/icon-bell-notification-inert.vue';
import CloseButton from '../partials/CloseButton.vue'

/**
 * @constants
 */

const route = useRoute();
const notificationSidebar = ref(null);

const isOpen = computed(() => notificationSidebar.value?.open);

function showOrHideSideBar() {
    !isOpen.value ? notificationSidebar.value?.showModal() : notificationSidebar.value?.close();
}

/**
 * @promises 
 */



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
</style>