<template>
    <TextAlert variant="info" class="mb-5">
        <template #alert-heading>
            Sending invitations
        </template> 

        <template #alert-content>
            Send your prospective members invitations by clicking the send button next to their names OR all at once.
        </template>
    </TextAlert>

    <form @submit.prevent="sendInvites(null, invitations)" v-if="invitations.length">
        <TransitionGroup name="content" tag="div" class="invitations">
            <div v-for="(invite, index) in invitations"
                :key="invite.id"
                class="invite" 
                :class="{
                    'existing-user': invite.type === Invitation.types.existing_user,
                    'created-invite': invite.user_id
                }"
            >
                <div v-if="!invite.user_id" class="display-flex items-center gap-2 flex-wrap">
                    <!-- Add placeholder for searched existing user here. -->
                    <SearchUserOverlay 
                        :book-club-id="route.params.bookclub" 
                        @user-selected="(userId) => selectedExistingUser(userId)"
                    />

                    <Input 
                        type="email"
                        placeholder="email"
                        @updated:model-value="(email) => invitations[index].email = email"
                    />
                </div>
                <!-- This means you made an invite but haven't sent it yet. -->
                <h3 v-else class="fancy text-stone-600 text-lg">
                    {{ invite.username }}
                </h3>

                <div class="flex gap-2">
                    <!-- Only show this if you aren't searching for a user -->
                    <Button v-if="(invite.status === Invitation.statuses.uninvited)"
                        type="button" 
                        class="btn btn-ghost"
                        :class="{submitting: 'btn-ghost'}"
                        :disabled="submitting"
                        @click="sendInvites([invite, index])"
                    >
                        <IconSend />
                    </Button>

                    <button
                        v-if="index !== 0 && index + 1 === invitations.length"
                        class="btn btn-red" 
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

            <div class="flex gap-2">
                <button v-if="invitations.length > 1" 
                    type="submit"
                    :disabled="submitting"
                    class="btn btn-tiny btn-submit text-sm"
                    :class="{submitting: 'btn-ghost'}"
                >
                    Send all invites
                </button>   

                <button 
                    class="btn btn-tiny btn-green text-sm"
                    type="button"
                    @click="previewEmailInvite">
                    Preview an invite email
                </button>
            </div>
        </div>
    </TransitionGroup>
    </form>

    <!-- Sent invitations go below -->
    <AsyncComponent :promise-factory="getInvitesForClubPromiseFactory" :subscription-key="INVITE_SUBSCRIPTION_KEY">
        <template #resolved>
            <div class="transition">
                <h3 class="text-2xl text-stone-600 fancy">Invited readers</h3>

                <div class="invitations sent" v-if="sentInvitations.length">
                    <div v-for="invite in sentInvitations" :key="invite.id" class="sent-invite">
                        <div>
                            <p class="fancy text-stone-600">
                                {{ invite.username || invite.email }}
                            </p>
                            <p class="text-sm text-stone-400">
                                Invited on: {{ invite.invited_on }}
                            </p>
                        </div>
                    </div>
                </div>

                <h4 v-else class="text-stone-500 fancy">
                    No invitations sent
                </h4>
            </div>
        </template>

        <template #loading>
            <div class="gradient fancy text-center text-xl loading-box">loading invitations</div>
        </template>
    </AsyncComponent>

    <Overlay ref="previewOverlay" v-if="!!previewEmailHTML">
        <template #overlay-main>
            <div v-html="previewEmailHTML"></div>
        </template>
    </Overlay>
</template>
<script setup>
import { ref } from 'vue';
import { useRoute } from 'vue-router';
import { Invitation, BaseInvitation } from '../../models/models';
import { db } from  '../../../../../services/db';
import { urls } from  '../../../../../services/urls';
import { PubSub } from '../../../../../services/pubsub';
import { createConfetti } from '../../../../../services/helpers';
import TextAlert from '@/components/feed/partials/textAlert/TextAlert.vue';
import SearchUserOverlay from './SearchUserOverlay.vue'
import IconSend from '@/components/svg/icon-send.vue';
import IconTrash from '@/components/svg/icon-trash.vue';
import Overlay from '@/components/feed/partials/overlay/Overlay.vue';
import AsyncComponent from '../../../partials/AsyncComponent.vue';
import { Input } from '@/lib/registry/default/ui/input';
import { Button } from '@/lib/registry/default/ui/button';

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

const previewEmailHTML = ref('');
const previewOverlay = ref(null);

const invitation = new BaseInvitation();
const invitations = ref([
    invitation
]);

const INVITE_SUBSCRIPTION_KEY = 'get-new-invites-for-club';

const sentInvitations = ref([]);

/**
 * @end_of_constants
 */


function closeOverlay() {
    const { dialogRef } = overlay.value;
    dialogRef.close();
}

// These two are pretty easy to get.
function addInvitationToForm() {
    let newInvitation = new BaseInvitation();
    invitations.value.push(newInvitation);
}

function removeInvitationFromForm() {
    let invs = invitations.value;    
    let lastInv = invs[invs.length - 1]
    lastInv.delete();
    // Delete it from the instance of BaseInvitations 
    // after you remove it from the ui.
    invitations.value.pop();
}

function selectedExistingUser(user) {
    let existingUserInvitation = new BaseInvitation();
    existingUserInvitation.user_id = user.user_id
    existingUserInvitation.type = Invitation.types.existing_user;
    existingUserInvitation.username = user.user_username
    invitations.value.push(existingUserInvitation);
}

/**
 * @definition helper function to fill up the payload object 
 * with correct values based on invite type.
 * @param {*} invite 
 * @param {*} payload 
 */
function inviteContactByType(invite, index, payload) {
    if (invite.type === Invitation.types.email) {
        payload.invites[index] = {}
        payload.invites[index].email = invite.email
    } else {
        payload.invites[index] = {}
        payload.invites[index].user_id = invite.user_id
    }
}

function populateInvitesForClub(invites) {
    if (!invites.length) return;
 
    invites.forEach((invite) => {
        const sentInvite = new BaseInvitation(invite);
        sentInvitations.value.push(sentInvite);
    });
}

function cleanUpOldInvitesAndUpdateSentInvitesList(invitesMap) {
    PubSub.publish('INVITE_SUBSCRIPTION_KEY', {});
    // Object.values(invitesMap).forEach(([id, invite]) => {
    //     // Oñ^2 but what are you going to do?
    //     let inviteInList = invitations.value.find((invitation) => invitation.id === id);
    //     let index = invitations.value.indexOf(inviteInList);
        
    //     // delete the old invite and remove it from the ui;
    //     inviteInList.delete();
    //     invitations.value.splice(index, 1);

    //     // then recreate it in the sent invites list
    //     const sentInvite = new BaseInvitation(invite)
    //     sentInvitations.value.push(sentInvite);
    // });
}

/**
 * @invite_promises
 * @desrciption functions for sending `mass` or `individual invites` and loading data 
 * @function sendInvites
 * @function loadInvites
 */
async function sendInvites(inviteMatrix, invitations) {
    submitting.value = true;
    let payload = {
        invites: {},
        book_club_id: route.params.bookclub,
    };

    if (inviteMatrix) {
        let invite = inviteMatrix[0];
        let index = inviteMatrix[1];

        inviteContactByType(invite, index, payload)
    } 

    // otherwise you are sending the whole form.
    if (!inviteMatrix && invitations?.length) {
        invitations.forEach((_invite, index) => inviteContactByType(_invite, index, payload));
    }


    db.post(urls.bookclubs.sendInvites(), payload, null, 
        async (res) => {
            await createConfetti();
            cleanUpOldInvitesAndUpdateSentInvitesList(res.invites);
        },
        (error) => {
            error.value = error;
        }
    ).then(() => {
        submitting.value = false;
    })
}


const getInvitesForClubPromiseFactory = () => db.get(urls.bookclubs.getInvitesForClub(route.params.bookclub), 
    null,
    false,
    (res) => {
        populateInvitesForClub(res.invites);
    }, 
    (error) => {
        console.log(error);
    }
);

async function previewEmailInvite() {
    db.get(urls.bookclubs.previewEmailInvitesForClub(route.params.bookclub, 'invite'), 
    {'is_preview': true}, false, 
    (res) => {
        previewEmailHTML.value = res.email;
        const { dialogRef } = previewOverlay.value;
        dialogRef.showModal();
    }, (err) => { console.log(err); });
};
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

    &.created-invite {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
}

.invite:last-of-type {
    border: solid 1px var(--stone-100);
}
</style>