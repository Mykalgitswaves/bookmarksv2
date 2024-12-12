<template>
    <div  v-if="totalChapters" class="paces-container">
        <AsyncComponent :promises="[clubPacePromise]">
            <template #resolved>
                    <div v-if="memberPaces.length">
                        <div class="flex text-sm">
                            <h4 class="text-stone-700">
                                <span class="text-indigo-500">{{memberPaces[0].username }}</span>
                                <br> is leading the club pace
                            </h4>

                            <button 
                                class="ml-auto text-sm text-indigo-500 underline fancy nowrap" 
                                @click="isViewingAllPaces = !isViewingAllPaces"
                            >
                                {{ isViewingAllPaces ? 'hide paces' : 'view all paces' }}
                            </button>
                        </div>

                        <div v-if="isViewingAllPaces" class="member-paces mt-2">
                            <div 
                                v-for="(member, index) in memberPaces" 
                                :key="member.id"
                                class="member-pace" 
                            >
                                <component :is="svgPaceMap[index]?.svg()" class="pace-icon"/> 

                                <div>
                                    <h4 class="text-stone-700">{{ member.username }}</h4>
                                    
                                    <p class="text-sm text-stone-500">{{ member.pace ? `is reading chapter ${member.pace}` : 'hasn\'t started yet' }}</p>
                                </div>

                                <button 
                                    v-if="member.id !== route.params.user && !hasMemberBeenPeerPressured[member.id]"
                                    type="button" 
                                    class="ml-auto btn btn-tiny btn-red text-sm" 
                                    @click="pressureReader(member)"
                                >
                                    pressure
                                </button>

                                <p class="ml-auto" v-else-if="member.id !== route.params.user && hasMemberBeenPeerPressured[member.id]">
                                    Peer pressured!
                                </p>

                                <!-- <canvas class="progress-bar" /> -->
                            </div>
                        </div>
                    </div>

                    <div v-else-if="!memberPaces.length" class="fancy text-stone-500 text-base">No ones started reading! (or made an update)</div>
            </template>
            <template #loading>
                <h4 class="text-center fancy text-stone-600">loading paces</h4>
            </template>
        </AsyncComponent>
    </div>
    <!-- Nerd stuff for you impatient readers. -->
    <SuccessToast v-if="toast" :toast="toast" :toast-type="Toast.TYPES.MESSAGE_TYPE" @dismiss="() => toast = null"/>
</template>
<script setup>
import { ref } from 'vue';
import { useRoute } from 'vue-router';
import { db } from '../../../../services/db';
import { urls } from '../../../../services/urls';
import IconRabbit from '@/components/svg/icon-rabbit.vue';
import IconTurtle from '@/components/svg/icon-turtle.vue';
import AsyncComponent from '../../partials/AsyncComponent.vue';
import { ClubNotification } from './notifications/models';
import SuccessToast from '../../../shared/SuccessToast.vue';

const props = defineProps({
    totalChapters: {
        type: Number,
    }
})

let memberPaces; 
let svgPaceMap = {};
const route = useRoute();
const isViewingAllPaces = ref(false);
const hasMemberBeenPeerPressured = ref({})
const toast = ref(null);

const clubPacePromise = db.get(urls.bookclubs.getClubPace(route.params.bookclub), null, false, (res) => {
    memberPaces = res.member_paces
    svgPaceMap = generateSvgPaceMap(memberPaces)
    
    // Go through and check to see if people have been peer pressured yet by another user in the club, 
    // in the allotted time frame. All handled by server.
    for (const member in memberPaces) {
        hasMemberBeenPeerPressured.value[member.id] = false;
    }

}, (err) => {
    console.error(err);
});

// create an svg map to assign fastest and slowest person with corresponding icons.
function generateSvgPaceMap(memberPaces) {
    if (!memberPaces?.length) {
        return {}
    }

    let svgMap =  {}
    let first = 0;
    let last = memberPaces.length -1;

    svgMap[first] = {
        svg: () => IconRabbit,
    }

    if(memberPaces.length < 2) {
        return svgMap
    }

    svgMap[last] = {
        svg: () => IconTurtle,
    }

    return svgMap
}



function pressureReader(member) {
    db.post(urls.bookclubs.peerPressureMember(route.params.bookclub), {
        member_id: member.id,
        notification_type: ClubNotification.types.peerPressure
    }, false, (res) => {
        console.log(res)
        const { notification } = res;
        // Create a toast for the user. 
        if (notification) {
            hasMemberBeenPeerPressured.value[member.id] = true;
            toast.value = ClubNotification.generateToastFromNotification(notification);
        }

    }, 
    (err) => {
        console.error(err);
    });
}

</script>
<style scoped>
    .member-paces {
        transition: all 250ms ease;
    }

    @starting-style {
        .member-paces {
           opacity: 0;
        }
    }

    .paces-container {
        padding: 8px 20px;
        border: 1px solid var(--stone-200);
        border-radius: var(--radius-sm);
        background-color: var(--stone-50);
        margin-top: 10px;
        min-height: 40px;
    }

    .member-pace {
        display: flex;
        justify-content: start;
        align-items: center;
        column-gap: 10px;

        /* 
        This is pretty gnarly, papdding fix if there isnt an icon.
        baseline support on https://caniuse.com/css-has 💁‍♂️
        */
        &:not(&:has(svg)) {
            padding-left: 49px;
        }
    }

    .pace-icon {
        transform: scale(80%);
        height: 40px;
        width: auto;
    }
</style>