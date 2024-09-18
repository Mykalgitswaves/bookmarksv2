<template>
    <TextAlert variant="info" class="mb-5">
        <template #alert-heading>
            Sending invitations
        </template> 

        <template #alert-content>
            Send your prospective members invitations either individually, by clicking the send button next to their names OR all at once by selecting multiple with the checkbox and clicking the blue "send invites" button below. 
        </template>
    </TextAlert>

    <form @submit.prevent="sendInvites(null, invitations)" v-if="invitations.length">
        <TransitionGroup name="content" tag="div" class="invitations">
            <div 
                v-for="(invite, index) in invitations"
                :key="invite.id"
                class="invite" 
                :class="{
                    'existing-user': invite.type === Invitation.types.existing_user
                }"
            >
                <div>
                    <div class="flex gap-2 items-center pb-4">
                        <label for="user_type" class="text-sm text-stone-500 block nowrap">
                            Add by:
                        </label>

                        <select class="select" name="" id="user_type" v-model="invite.type">
                            <option value="email">email</option>
                            <option value="existing_user">existing user</option>
                        </select>
                    </div>
                    
                    <input v-if="invite.type === Invitation.types.email" 
                        class="input border-2 fancy input--invitation w-100 pl-5 py-2"
                        type="email" 
                        id="email" 
                        :name="invite.id"
                        placeholder="email" 
                        v-model="invitations[index].email" 
                    >

                    <!-- Add placeholder for searched existing user here. -->
                    <SearchUserOverlay 
                        v-if="invite.type === Invitation.types.existing_user"
                        :book-club-id="route.params.bookclub" 
                        @user-selected="(userId) => selectedExistingUser(userId)"
                    />
                </div>

                <p class="italic text-stone-600 text-center">{{ invite.status }}</p>

                <div class="flex gap-2">
                    <!-- Only show this if you aren't searching for a user -->
                    <button v-if="(invite.status === Invitation.statuses.uninvited)"
                        type="button"
                        :disabled="submitting"
                        class="btn btn-small btn-ghost text-indigo-500"
                        :class="{submitting: 'btn-ghost'}"
                        @click="sendInvites(invite)"
                    >
                        <IconSend />
                    </button>

                    <button
                        v-if="index !== 0 && index + 1 === invitations.length"
                        class="btn btn-red btn-tiny" 
                        type="button"
                        @click="removeInvitationFromForm()" 
                    >
                        <IconTrash />
                    </button>
                </div>
            </div>
        

        <div class="toolbar--between w-border">                
            <button 
                class="btn btn-tiny btn-green text-sm"
                type="button"
                @click="addInvitationToForm">
                Invite another person
            </button>

                <button v-if="invitations.length > 1" 
                    type="submit"
                    :disabled="submitting"
                    class="btn btn-tiny btn-submit text-sm"
                    :class="{submitting: 'btn-ghost'}"
                >
                Send all invites
            </button>   
        </div>
    </TransitionGroup>
    </form>

</template>
<script setup>
import { ref, computed } from 'vue';
import { useRoute } from 'vue-router';
import { Invitation, BaseInvitation } from '../../models/models';
import { db } from  '../../../../../services/db';
import { urls } from  '../../../../../services/urls';
import TextAlert from '@/components/feed/partials/textAlert/TextAlert.vue';
import SearchUserOverlay from './SearchUserOverlay.vue'
import IconSend from '@/components/svg/icon-send.vue';
import IconTrash from '@/components/svg/icon-trash.vue';

const props = defineProps({
    memberData: {
        type: Object,
        required: false,
    }
});

/**
 * @constants
 */
const submitting = ref(false);
const isShowingSearchOverlay = ref(false);
const route = useRoute()

const invitation = new BaseInvitation();
const invitations = ref([
    invitation
]);
/**
 * @end_of_constants
 */

// TODO: finish searching for user before being able to add a new one.

// Not overengineering i promise. Using a computed variable to auto update truthyness of
// whether any of our invites should see the search bar. Used for css nerdage below.
// To give us enough room for the whole search bar.
// const isSearchingForUser = computed(() => {
//     let result = {};
//     invitations.value.forEach((invite, index) => {
//         // If they have not sent an invite and have existing_user selected
//         result[index + 1] = !!(
//             invite.type === Invitation.types.existing_user && invite.status === Invitation.statuses.uninvited
//         )
//     });
//     return result;
// });

// These two are pretty easy to get.
function addInvitationToForm() {
    let newInvitation = new BaseInvitation();
    invitations.value.push(newInvitation);
}

function removeInvitationFromForm() {
    let invs = invitations.value;    
    let lastInv = invs[invs.length - 1]
    BaseInvitation.delete(lastInv.id);
    // Delete it from the instance of BaseInvitations 
    // after you remove it from the ui.
    invitations.value.pop();
}

/**
 * @definition helper function to fill up the payload object 
 * with correct values based on invite type.
 * @param {*} invite 
 * @param {*} payload 
 */
function inviteContactByType(invite, payload) {
    invite.type === Invitation.types.email ? 
        payload.emails.push(invite.email) :
        payload.user_ids.push(invite.user_id);
}

/**
 * @definition Look through emails by type and status to find those who match the emails submitted via request so we can update the js objects floating around in the ui. Probably not the best way to do this but unless we return a dictionary with more shit in it you never know.
 * @param {*} payload 
 */
function updateInvitesStatus(payload){
    let emails = payload.emails;
    let userIds = payload.user_ids;

    invitations.value.forEach((invite) => {
        if ((
                emails.length && 
                invite.type === Invitation.types.email &&  
                emails.includes(invite.email) && 
                invite.status === Invitation.statuses.uninvited
            ) || (
                usersIds.length && 
                invite.type === Invitation.types.existing_user && 
                userIds.includes(invite.user_id) &&
                invite.status === Invitation.statuses.uninvited
            ) 
        ) {
            invite.status = Invitation.statuses.invited;
        }
    });
}

function selectedExistingUser(userId) {
    console.log(userId);
}

/**
 * @invite_promises
 * @desrciption functions for sending `mass` or `individual invites` and loading data 
 * @function sendInvites
 * @function loadInvites
 */
    async function sendInvites(invite, invitations) {
        submitting.value = true;
        let payload = {
            user_ids: [],
            emails: [],
            book_club_id: route.params.bookclub,
        };

        if (invite) {
            inviteContactByType(invite, payload)
        } 

        // otherwise you are sending the whole form.
        if (!invite && invitations?.length) {
            invitations.forEach((_invite) => inviteContactByType(_invite, payload));
        }


        db.post(urls.bookclubs.sendInvites(), payload, null, 
            (res) => {
                updateInvitesStatus(payload);
            },
            (error) => {
                error.value = error;
            }
        ).then(() => {
            submitting.value = false;
        })
    }
/**
 * @end
 */
</script>
<style scoped>
.invitations {
    max-width: 768px;
    padding-bottom: 14px;
    padding-top: 14px;
    margin-left: auto; 
    margin-right: auto;
    display: grid;
    row-gap: 14px;
}

.invite {
    display: grid;
    align-items: end;
    grid-template-columns: 1fr min-content min-content;
    column-gap: 8px;

    &.existing-user {
        /* grid-template-columns: 16px 1fr; */
    }
}

.invite:last-of-type {
    border: solid 1px var(--stone-100);
}
</style>