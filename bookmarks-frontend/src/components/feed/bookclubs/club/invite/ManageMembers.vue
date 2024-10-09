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

    <div>

    </div>
</template>
<script setup>
import { ref } from 'vue';
import { useRoute } from 'vue-router';
import { Invitation, BaseInvitation } from '../../models/models';
import { db } from  '../../../../../services/db';
import { urls } from  '../../../../../services/urls';
import TextAlert from '@/components/feed/partials/textAlert/TextAlert.vue';
import { Member } from '../../models/models';

const members = ref([]);
const route = useRoute();

/**
 * @loadMembersPromise
 */
function loadMembers() {
    debugger;
    let url = urls.bookclubs.getMembersForBookClub(route.params.bookclub, route.params.user);
    db.get(url, null, false, 
    (res) => {
        
    }, 
    (err) => {
        console.log(err);
    });
};

/**
 * @load
 */
loadMembers();

</script>