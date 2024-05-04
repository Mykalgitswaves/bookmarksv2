<template>
    <div class="collaborator">
        <!-- We need to replace this with actual profile images -->
        <svg class="extra small-profile-image" xmlns="http://www.w3.org/2000/svg" version="1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:svgjs="http://svgjs.dev/svgjs" viewBox="0 0 700 700" width="50" ><defs><linearGradient gradientTransform="rotate(183, 0.5, 0.5)" x1="50%" y1="0%" x2="50%" y2="100%" id="ffflux-gradient"><stop stop-color="hsl(267, 172%, 20%)" stop-opacity="1" offset="0%"></stop><stop stop-color="hsl(100, 100%, 80%)" stop-opacity="1" offset="100%"></stop></linearGradient><filter id="ffflux-filter" x="-20%" y="-20%" width="140%" height="140%" filterUnits="objectBoundingBox" primitiveUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
            <feTurbulence type="fractalNoise" baseFrequency="0.005 0.003" numOctaves="1" seed="196" stitchTiles="stitch" x="0%" y="0%" width="100%" height="100%" result="turbulence"></feTurbulence>

            <feGaussianBlur stdDeviation="20 0" x="0%" y="0%" width="100%" height="100%" in="turbulence" edgeMode="duplicate" result="blur"></feGaussianBlur>

            <feBlend mode="color-dodge" x="0%" y="0%" width="100%" height="100%" in="SourceGraphic" in2="blur" result="blend"></feBlend>

            </filter></defs><rect width="100%" height="100%" fill="url(#ffflux-gradient)" filter="url(#ffflux-filter)"></rect>
        </svg>

        <div>
            <h4 class="collaborator-username">{{ friend?.username || currentUserName }}</h4>

            <!-- <p id="role" class="collaborator-role">role: {{ friend?.role || role || 'unassigned' }}</p>   -->
        </div>
        <!-- Only owner can remove contributors -->

        <!-- Stuff for adding permissions to your friends -->
        <form v-if="isSuggested && !['owner', 'contributor'].includes(role)" class="ml-auto collab-type-form" @submit.prevent="setFriendAsCollaboratorType">
            <select class="collab-select" name="" id="collaborator-types" v-model="collabType">
                <option value="contributor">contributor</option>

                <option value="member">member</option>
            </select>

            <button type="submit" class="btn btn-green-100" @click="setFriendRoleOnBookshelf(friend.id, collabType)">add</button>

            <button type="button" class="btn btn-red-100" @click="$emit('remove-friend-from-suggested', friend?.id)">ignore</button>
        </form>

        <form v-if="!isSuggested && currentUserIsAdmin" class="ml-auto collab-type-form" @submit.prevent="removeFromBookshelf()">
            <button type="submit"
                class="btn ml-auto"
                :class="{ 
                    'btn-danger': role === 'collaborator', 
                    'btn-role-disabled': role === 'owner', // Owner cannot be removed
                    'btn-red-100': ['contributor', 'member'].includes(role),
                }"
                :disabled="role === 'owner'"
            >
                Remove
            </button>
        </form>
    </div>
</template>
<script setup>
import { ref } from 'vue'
import { db } from '../../../services/db';
import { urls } from '../../../services/urls';
import { routeLocationKey } from 'vue-router';

const props = defineProps({
    role: {
        type: String,
        required: false,
        default: 'collaborator',
    },
    friend: {
        type: Object,
        required: true,
    },
    bookshelfId: {
        type: String,
        required: true,
    },
    currentUserIsAdmin: {
        type: Boolean,
        required: false,
        default: false,
    },
    isSuggested: {
        type: Boolean,        
        default: false,
    }
});

const emit = defineEmits(['added-member', 'added-contributor', 'removed-contributor', 'removed-member']);
const collabType = ref('none');
const hasBeenAdded = ref(false);

async function setFriendRoleOnBookshelf() {
    console.log('firing this shit');
    try {
        if(collabType.value === 'collaborator'){
            await db.put(urls.rtc.setContributorOnShelf(props.bookshelfId), 
                {'contributor_id': props.friend.id}, true).then((res) => {
                if(res?.status === 200){
                    emit('added-collaborator', props.friend.id);
                }
            })
        } else if(collabType.value === 'member'){
            await db.put(urls.rtc.setMemberOnShelf(props.bookshelfId), 
               {'member_id': props.friend.id}, true).then((res) => {
                if(res?.status === 200){
                    emit('added-member', props.friend.id);
                }
            })
        }
        
        hasBeenAdded.value =  true;
    } catch(err) {
        console.log(err);
    }
}

async function removeFromBookshelf() {
    if (props.friend.role === 'contributor') {
        await db.put(urls.rtc.removeContributorFromShelf(props.bookshelfId), 
            { 'contributor_id': props.friend.user_id }).then(() => {

            emit('removed-contributor', props.friend.user_id);
        });
    } else if (props.friend.role === 'member') {
        await db.put(urls.rtc.removeMemberFromShelf(props.bookshelfId), 
            { 'member_id': props.friend.user_id }).then(() => {
                
            emit('removed-member', props.friend.user_id);
        });
    }
}

</script>
<style scoped>
    .collaborator {
        margin-right: auto;
        padding-top: var(--padding-sm);
        padding-bottom: var(--padding-sm);
        display: flex;
        align-items: center;
        justify-content: space-between;
        min-width: 280px;
        text-align: start;
        column-gap: 12px;
    }

    .collaborator-role {
        color: var(--stone-500);
    }

    .collaborator-text {
        align-self: start;
    }

    .collaborator-username {
        font-size: var(--font-lg);
        font-weight: 500;
        color: var(--stone-800);
    }

    .btn-danger {
        background-color: var(--red-100);
        color: var(--red-700);
        border-radius: var(--radius-sm);
        padding-left: 12px;
        padding-right: 12px;
    }

    .btn-role-disabled {
        color: var(--stone-400);
    }

    .ml-auto {
        margin-left: auto;
    }

    .collab-select {
        min-width: fit-content;
        border: 1px solid var(--stone-100);
        border-radius: var(--radius-sm);
        color: var(--stone-700);
        font-size: var(--font-sm);
    }

    .collab-type-form {
        display: flex;
        column-gap: 12px;
    }

    .btn-green-100 {
        background-color: var(--green-100);
        color: var(--green-700);
        border-radius: var(--radius-sm);
        padding-left: 12px;
        padding-right: 12px;
    }

    .btn-green-100:hover {
        background-color: var(--green-200);
    }

    .btn-red-100 {
        background-color: var(--red-100);
        color: var(--red-700);
        border-radius: var(--radius-sm);
        padding-left: 12px;
        padding-right: 12px;
    }

    .btn-red-100:hover {
        background-color: var(--red-200);
    }
</style>