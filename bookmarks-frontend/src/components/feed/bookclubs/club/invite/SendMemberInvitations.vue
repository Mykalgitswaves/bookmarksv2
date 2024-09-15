<template>
    <TextAlert>
        <template #alert-heading>

        </template>
        <template #alert-content>

        </template>
    </TextAlert>

    <form @submit.prevent>
        <TransitionGroup name="content" tag="div" class="invitations">
            <div class="invite"
                v-for="(invite, index) in invitations"
                :key="index"
            >
                <input type="checkbox" v-model="invite.selected" style="margin-top: 4px;">

                <input type="text" v-model="invite.email" class="input border-2 fancy input--invitation">

                <p class="italic text-stone-600 text-center">{{ invite.status }}</p>

                <button v-if="invite.status === Invitation.statuses.uninvited"
                    type="submit"
                    class="btn btn-small btn-ghost text-indigo-500"
                >
                    <IconSend />
                </button>
            </div>
        

        <div class="toolbar--between w-border">                
            <button 
                class="btn btn-tiny btn-green text-sm"
                type="button"
                @click="addInvitationToForm">
                Invite another person
            </button>

            <button
                class="btn btn-red btn-tiny" 
                type="button"
                @click="removeInvitationFromForm()" 
            >
                remove
            </button>
        </div>
    </TransitionGroup>
    </form>

</template>
<script setup>
import { ref } from 'vue';
import { Invitation } from '../../models/models';
import IconSend from '@/components/svg/icon-send.vue';
import TextAlert from '@/components/partials/TextAlert.vue';

const props = defineProps({
    memberData: {
        type: Object,
        required: false,
    }
});

let inviteCount = 1;

const baseInvitation = {
        id: inviteCount,
        selected: false,
        email: '',
        status: Invitation.statuses.uninvited
}

const invitations = ref([
    baseInvitation
]);

function addInvitationToForm() {
    inviteCount += 1;
    invitations.value.push(baseInvitation)
}

function removeInvitationFromForm() {
    invitations.value.pop();
}
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
    align-items: center;
    grid-template-columns: 16px 1fr 180px min-content;
    column-gap: 8px;
}

.invite:last-of-type {
    border: solid 1px var(--stone-100);
}
</style>