<template>
    <TextAlert variant="warning" class="mb-5">
        <template #alert-heading>
            Managing members
        </template> 

        <template #alert-content>
            <h3 class="text-xl text-red-500">🦅 DANGER ZONE 🦅</h3>
            Manage members for your club, grant and revoke permissions and club access. 
        </template>
    </TextAlert>
    
    <AsyncComponent :promises="[loadMembersPromise]">
        <template #resolved>
            <h3 class="text-2xl text-stone-600 fancy">Members</h3>

            <div class="invitations sent" v-if="members.length">
                <div v-for="(member, index) in members" :key="member.id" class="member">
                    <div>
                        <p class="fancy text-stone-600">
                            {{ member.username }}
                        </p>

                        <p class="text-sm text-stone-400">
                            {{ member.email }}
                        </p>
                    </div>
                    
                    <button 
                        class="btn btn-ghost btn-tiny text-sm" 
                        type="button" 
                        @click="removeMemberFromClub(member.id, index)"
                    >
                        remove
                    </button>
                </div>
            </div>

            <div v-else>
                <h3 class="text-lg text-stone-400">
                    No members have joined this club yet
                </h3>
            </div>
        </template>

        <template #loading>
            <div class="gradient fancy text-center text-xl loading-box">
                Loading members
            </div>
        </template>
    </AsyncComponent>
</template>
<script setup>
import { ref } from 'vue';
import { useRoute } from 'vue-router';
import { Invitation, BaseInvitation } from '../../models/models';
import { db } from  '../../../../../services/db';
import { navRoutes, urls } from  '../../../../../services/urls';
import TextAlert from '@/components/feed/partials/textAlert/TextAlert.vue';
import { Member } from '../../models/models';
import AsyncComponent from '../../../partials/AsyncComponent.vue';

let members = [];
const route = useRoute();

/**
 * @promises
 */

const loadMembersPromise = db.get(urls.bookclubs.getMembersForBookClub(route.params.bookclub, route.params.user), null, false, 
    (res) => {
        members = res.members;
    }, 
    (err) => {
        console.log(err);
    }
);

function removeMemberFromClub(user_id, vForIndex) {
    // vForIndexes are not 0 based, their starting index is 1.
    let index = vForIndex - 1;
    if (window.confirm('Are you sure you want to remove this member')) {
        db.delete(
            urls.bookclubs.removeMemberFromBookClub(
                route.params.bookclub,
            ), {user_id: user_id}, false, 
            () => {
                members.value.splice(index, 1);
            }, 
            (err) => {
                console.log(err);
            }
        );
    }
}
</script>
<style scoped>
.member {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 4px;
}
</style>