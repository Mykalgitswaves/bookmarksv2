<template>
    <div class="bookclub-header">
            <div>
                <h1 class="text-3xl fancy text-stone-700">
                    Member settings
                </h1>
                
                <p class="text-stone-500 mt-5">
                    Send invites, manage your club members, admin stuff.  
                </p>
            </div>
    </div>

    <div class="club-main-padding">
        <!-- For nav -->
        <div role="toolbar" class="toolbar flex justify-between items-center">
            <button 
                type="button"
                class="btn btn-toolbar"
                :class="{'active': currentView === views.invitations}"
                @click="currentView = views.invitations;"
            >
                Invitations:
                
            </button>

            <button 
                type="button"
                class="btn btn-toolbar"
                :class="{'active': currentView === views.manageMembers}"
                @click="currentView = views.manageMembers; $emit('view-changed', views.manageMembers)"
            >
                Manage members: <i>{{ memberCount || '0' }}</i>
            </button>
        </div>
    </div>

    <MemberInvitations v-if="currentView === views.invitations" />

    <ManageMembers v-if="currentView === views.manageMembers" />

    <div class="mobile-menu-spacer sm:hidden"></div>
</template>
<script setup>
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { navRoutes } from '../../../../../services/urls';
import BackBtn from '../../../partials/back-btn.vue';
import MemberInvitations from './MemberInvitations.vue';
import ManageMembers from './ManageMembers.vue';

const props = defineProps({
    club: {
        type: Object,
        required: true,
    }
});

/**
 * @constants
 */

const views = {
    invitations: 'invitations',
    manageMembers: 'manage-members',
}; 

let data;
let pendingInvitations;
let memberCount;
const router = useRouter();
const route = useRoute();

/**
 * @end_of_constants
 */

console.log(props.club)

/**
 * ----------------------------------------------------------------------------
 * @current_view_requirements
 * @todo
 * we need a clever way to determine whether a club has outstanding 
 * invites so that we can auto route to the correct view. `invitations`
 * for new clubs without any pending invites, and `manage members` for
 * clubs with more than zero members
 * ----------------------------------------------------------------------------
 * For now initialize to `invitations`
 */
 
const currentView = ref(views.invitations);

</script>