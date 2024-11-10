<template>
    <div class="paces-container">
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

                            <!-- <canvas class="progress-bar" /> -->
                        </div>
                    </div>
                </div>
                <div v-else class="fancy text-stone-500 text-xl">No ones started reading! (or made an update)</div>
            </template>
            <template #loading>
                <h4 class="text-center fancy text-stone-600">loading paces</h4>
            </template>
        </AsyncComponent>
    </div>
</template>
<script setup>
import { ref } from 'vue';
import { useRoute } from 'vue-router';
import { db } from '../../../../services/db';
import { urls } from '../../../../services/urls';
import IconRabbit from '@/components/svg/icon-rabbit.vue';
import IconTurtle from '@/components/svg/icon-turtle.vue';
import AsyncComponent from '../../partials/AsyncComponent.vue';

const props = defineProps({
    totalChapters: {
        type: Number,
    }
})

let memberPaces; 
let svgPaceMap = {};
const route = useRoute();
const isViewingAllPaces = ref(false);

const clubPacePromise = db.get(urls.bookclubs.getClubPace(route.params.bookclub), null, false, (res) => {
    memberPaces = res.member_paces
    svgPaceMap = generateSvgPaceMap(memberPaces)
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