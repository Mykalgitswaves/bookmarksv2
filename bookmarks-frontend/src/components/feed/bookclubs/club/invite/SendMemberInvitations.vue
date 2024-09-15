<template>
    <TextAlert variant="info" class="mb-5">
        <template #alert-heading>
            Sending invitations
        </template> 

        <template #alert-content>
            Send your prospective members invitations either individually, by clicking the send button next to their names OR all at once by selecting multiple with the checkbox and clicking the blue "send invites" button below. 
        </template>
    </TextAlert>

    <form @submit.prevent="submitInvites" v-if="invitations.length">
        <TransitionGroup name="content" tag="div" class="invitations">
            <div 
                v-for="(invite, index) in invitations"
                :key="invite.id"
                class="invite" 
                :class="{
                    'existing-user': invite.type === Invitation.types.existing_user
                }"
            >
                <input type="checkbox" v-model="invite.selected">

                <div>
                    <div class="flex gap-2 items-center pb-4">
                        <label for="user_type" class="text-sm text-stone-500 block nowrap">
                            Add by:
                        </label>

                        <select class="select" name="" id="user_type" v-model="invite.type">
                            <option value="email">email</option>
                            <option value="existing-user">existing user</option>
                        </select>
                    </div>
                    
                    <input v-if="invite.type === Invitation.types.email" 
                        class="input border-2 fancy input--invitation w-100 pl-5"
                        type="email" 
                        id="email" 
                        :name="invite.id"
                        placeholder="email" 
                        v-model="invitations[index].email" 
                    >

                    <!-- Add search by existing user here. -->
                </div>

                <p class="italic text-stone-600 text-center">{{ invite.status }}</p>

                <div class="flex gap-2">
                    <!-- Only show this if you aren't searching for a user -->
                    <button v-if="(invite.status === Invitation.statuses.uninvited) 
                        && !isSearchingForUser[index]"
                        type="button"
                        class="btn btn-small btn-ghost text-indigo-500"
                        @click="submitInvites(index)"
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

            <button v-if="invitations.length > 1" type="submit" class="btn btn-tiny btn-submit text-sm">
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
import IconSend from '@/components/svg/icon-send.vue';
import IconTrash from '@/components/svg/icon-trash.vue';
import TextAlert from '@/components/feed/partials/textAlert/TextAlert.vue';

const props = defineProps({
    memberData: {
        type: Object,
        required: false,
    }
});

const route = useRoute()
const { params } = route;
let invitation = new BaseInvitation();

const invitations = ref([
    invitation
]);

// Not overengineering i promise. Using a computed variable to auto update truthyness of
// whether any of our invites should see the search bar. Used for css nerdage below.
// To give us enough room for the whole search bar.
let isSearchingForUser = computed(() => {
    
});

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
 * @invite_promises
 * @desrciption functions for sending `mass` or `individual invites` and loading data 
 * @function sendInvites
 * @function loadInvites
 */
    async function sendInvites(selectedIndex, data) {
        let payload = {
            user_ids: [],
            emails: [],
            bookclub_id: params.bookclub,
        };

        let rawInvitations = invitations.value;
        // Note index in a template v-for loop is 1 based.
        for(let index = 0; i < rawInvitations.length; i++) {
            let invitation = rawInvitations[index];
            if (selectedIndex && selectedIndex === index) {
                // Break out of loop early in case you are only looking for a specific index.
                emails.push(invitation.email);
                break;
                // Otherwise throw em all in there.
            } else if (!selectedIndex) {
                emails.push(invitation.email)
            }
        };    

        db.post(urls.bookclubs.sendInvites(), payload, null, 
            (res) => {
                
            },
            (error) => {
                
            }
        )
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
    grid-template-columns: 16px 1fr min-content min-content;
    column-gap: 8px;

    &.existing-user {
        grid-template-columns: 16px 1fr;
    }
}

.invite:last-of-type {
    border: solid 1px var(--stone-100);
}
</style>