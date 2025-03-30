<template>
    <div  v-if="totalChapters" class="paces-container" :class="{'min-h-200': startOpen && memberPaces?.length > 1}">
        <AsyncComponent :promises="[clubPacePromise]">
            <template #resolved>
                    <div v-if="memberPaces.length">
                        <div class="flex text-sm">
                            <h4 class="text-stone-700">
                                <span class="text-indigo-500">{{memberPaces[0].username }}</span>
                                <br> is leading the club pace
                            </h4>

                            <button 
                                v-if="!startOpen"
                                class="ml-auto text-sm text-indigo-500 underline fancy nowrap" 
                                @click="isViewingAllPaces = !isViewingAllPaces"
                            >
                                {{ isViewingAllPaces ? 'hide paces' : 'view all paces' }}
                            </button>
                        </div>

                        
                        <div v-if="isViewingAllPaces || startOpen || statusForClub.clubFinishedWithCurrentBook" 
                            class="member-paces mt-2"
                        >
                            <div 
                                v-for="(member, index) in memberPaces" 
                                :key="member.id"
                                class="member-pace" 
                            >
                                <component :is="svgPaceMap[index]?.svg()" class="pace-icon"/> 

                                <div>
                                    <h4 class="text-stone-700">{{ member.username }}</h4>
                                    
                                    <p v-if="!member?.is_finished_reading" class="text-sm text-stone-500">{{ member.pace ? `is reading chapter ${member.pace} of ${props.totalChapters}` : 'hasn\'t started yet' }}</p>
                                    <p v-else class="text-sm text-stone-500">Finished reading! 🎉</p>
                                </div>

                                <div class="pace-line" 
                                    :style="{
                                        width: statusForClub.clubFinishedWithCurrentBook  ? '100%' : generateProgressBarWidthForMember(member),
                                        height: '4px',
                                        backgroundColor: member?.is_finished_reading ? 'var(--green-300)' : 'var(--indigo-300)',
                                        borderRadius:  '4px',
                                        position: 'absolute',
                                        bottom: '-8px',
                                        left: 0,
                                    }"
                                ></div>

                                <button 
                                    v-if="member.id !== route.params.user && !hasMemberBeenPeerPressured[member.id]"
                                    type="button" 
                                    class="ml-auto btn btn-tiny btn-red text-sm" 
                                    @click="pressureReader(member)"
                                >
                                    pressure
                                </button>

                                <p class="ml-auto fancy text-stone-500" v-else-if="member.id !== route.params.user && hasMemberBeenPeerPressured[member.id]">
                                    🪄 Peer pressured! ✨
                                </p>

                                <!-- <canvas class="progress-bar" /> -->
                            </div>
                        </div>
                    </div>
                    
                    <div v-else-if="memberPaces.length === 1" class="grid place-center gap-y-4">
                        <h5 class="text-stone-600 fancy text-center">
                            Its just you, add some friends and start yapping!
                        </h5>

                        <button 
                            type="button"
                            class="btn text-sm btn-tiny btn-nav fancy ml-auto mr-auto" 
                            @click="$router.push(
                                navRoutes.bookClubSettingsManageMembersIndex(user.id, $route.params.bookclub)
                            )"
                        >
                            Add members
                        </button>
                    </div>

                    <div v-else-if="!memberPaces.length" 
                        class="fancy text-stone-500 text-base"
                    >   
                        <span v-if="!statusForClub.clubFinishedWithCurrentBook">
                            No ones started reading! (or made an update)
                        </span>
                        
                        <span class="block text-sm" v-if="statusForClub.clubFinishedWithCurrentBook">
                            No one posted but the clubs done reading 🧐?
                        </span>
                    </div>
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
// Vue
import { defineAsyncComponent, ref, computed } from 'vue';
import { useRoute } from 'vue-router';
// stores
import { useCurrentUserStore } from '@/stores/currentUser';
// services
import { db } from '../../../../services/db';
import { urls } from '../../../../services/urls';
import { ClubNotification } from './notifications/models';
import { Toast } from '../../../shared/models';
import { navRoutes } from '@/services/urls';
// Components
import AsyncComponent from '../../partials/AsyncComponent.vue';
// lazy loaded components
const IconRabbit = defineAsyncComponent(() => import('@/components/svg/icon-rabbit.vue'));
const IconTurtle = defineAsyncComponent(() => import('@/components/svg/icon-turtle.vue'));
const SuccessToast  = defineAsyncComponent(() => import('../../../shared/SuccessToast.vue'));
// --------------------------------------------

const props = defineProps({
    totalChapters: {
        type: Number,
    },
    startOpen: {
        type: Boolean,
        default: false,
    }
})

let memberPaces; 
let svgPaceMap = {};
const route = useRoute();
const { bookclub } = route.params;
const isViewingAllPaces = ref(false);
const hasMemberBeenPeerPressured = ref({})
const toast = ref(null);

const store = useCurrentUserStore();
const { user } = store;

const statusForClub = computed(() => {
    const clubRel = user.clubs[bookclub];

    if(!clubRel) {
        console.warn('badbadnotgood status for club');
        return false
    }

    return clubRel;
});

const clubPacePromise = db.get(urls.bookclubs.getClubPace(route.params.bookclub), null, false, (res) => {
    memberPaces = res.member_paces;

    memberPaces.forEach((member) => {
        if (member.pace === 99999) {
            member.is_finished_reading = true;
        }
    })
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
    hasMemberBeenPeerPressured.value[member.id] = true;
    db.post(urls.bookclubs.peerPressureMember(route.params.bookclub), {
        member_id: member.id,
        notification_type: ClubNotification.types.peerPressure
    }, false, (res) => {
        const { notification } = res;
        // Create a toast for the user. 
        if (notification) {
            toast.value = ClubNotification.generateToastFromNotification(notification);
        }

    }, 
    (err) => {
        console.error(err);
    });
}

function generateProgressBarWidthForMember(member) {
    if (member.pace === 99999) return '100%';

    return `${(member.pace / props.totalChapters) * 100}%`
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
        background-color: var(--surface-primary);
        margin-top: 10px;
        min-height: 40px;
    }

    .member-pace {
        display: flex;
        justify-content: start;
        align-items: center;
        column-gap: 10px;
        position: relative;
        margin-bottom: 14px;

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

    .min-h-200 {
        min-height: 200px;
    }
</style>