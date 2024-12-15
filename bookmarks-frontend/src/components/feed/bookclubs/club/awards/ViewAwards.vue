<template>
<dialog ref="awardsModal" class="awards-menu">
    <div class="pt-5">
        <CloseButton 
            class="ml-auto" 
            @close="() => {
                awardsModal.close();
                postModalData = null
            }"
        />
    </div>

    <!-- Default is viewing all the awards not relative to a specific post -->
    <div>
        <!-- maybe we want to use async component here, idk though. -->
        <AsyncComponent :promises="[getAwardsPromise]"> 
            <template #resolved>
                <div class="award-grid">
                    <div v-for="(category, key) in awards" 
                        :key="index"
                    >
                        <h3 class="text-xl text-stone-700 fancy text-start mb-5">
                            {{ key }}
                        </h3>

                        <div class="award-type" v-if="category">
                            <div v-for="award in category" :key="award.id">
                                <div class="award"
                                    :class="{
                                        'granted': awardStatuses[award.id].status === Award.statuses.grantable,
                                        'expired': awardStatuses[award.id].status === Award.statuses.expired,
                                        'loading': awardStatuses[award.id].status === Award.statuses.loading,
                                    }"
                                    @click="grantAwardToPost(postId, award, [award.current_uses, award.allowed_uses])"
                                >
                                    <span class="award-front">
                                        <component class="award-icon" v-if="ClubAwardsSvgMap[award.cls]" :is="ClubAwardsSvgMap[award.cls]()" />

                                        <p class="award-title">{{ award.name }}</p>

                                        <p class="award-description">{{  award.description }}</p>
                                    </span>
                                </div>
                                
                                <p class="text-xs bold text-stone-500 text-center">
                                    {{ `${award.current_uses} granted on this post, ${award.allowed_uses - award.current_uses} remaining` }}
                                </p>

                                <button 
                                    v-if="award.current_uses > 0"
                                    type="button" 
                                    class="text-xs text-red-500" 
                                    @click="ungrantAwardFromPost(postId, award)"
                                >
                                    Ungrant
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </template>

            <template #loading>
                <LoadingCard />
            </template>
        </AsyncComponent>
    </div>
</dialog>
</template>
<script setup>
import { urls } from '../../../../../services/urls';
import { db } from '../../../../../services/db';
import { ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { Award } from './awards.js';
import CloseButton from '../../../partials/CloseButton.vue';
import LoadingCard from '@/components/shared/LoadingCard.vue';
import AsyncComponent from '../../../partials/AsyncComponent.vue';
import { ClubAwardsSvgMap } from '../awards/awards';
import { PubSub } from '../../../../../services/pubsub.js';

const awardStatuses = ref({});
let postId;
let awards = {};
let awardNames = [];

const loading = ref(false);
const loaded = ref(false);
const route = useRoute();
const { bookclub } = route.params

db.get(urls.bookclubs.getAwards(bookclub), null, false, (res) => {
    awards = res.awards;
    loaded.value = true;
});

const getAwardsPromise = db.get(urls.bookclubs.getAwards(bookclub), 
    { 
        post_id: postId,
        current_uses: true,
    },
    false, 
    (res) => {
        let _awards = res.awards;
        let awardsByType = {};
        
        let awardLimit = _awards.length;
        let index = 0;

        // This is marginally faster than a normal for loop.
        while (index < awardLimit) {
            awardStatuses.value[_awards[index].id] = {};
            if (!awardsByType[_awards[index].type]) {
                awardsByType[_awards[index].type] = []
                awardNames.push(_awards[index].type);
            }

            // two conditions here, either you can grant awards or you cant
            if (_awards[index].current_uses === _awards[index].allowed_uses) {
                awardStatuses.value[_awards[index].id].status = Award.statuses.expired;
            }
            
            if (_awards[index].current_uses > 0 && _awards[index].current_uses < _awards[index].allowed_uses) { 
                awardStatuses.value[_awards[index].id].status = Award.statuses.grantable;
            };

            index += 1;
        };

        // Set the awards by type.
        Object.keys(awardsByType).forEach((key) => {
            awardsByType[key] = (_awards
                .filter((award) => award.type === key)
                .sort((a, b) => a.current_uses - b.current_uses)
            );
        });

        awards = awardsByType;
        loaded.value = true;
});

const awardsModal = ref(null);
const isOpen = ref(false);

/**
 * @UI_functions
 */

function handleClickOutside(event){
    if (
        awardsModal.value 
        && awardsModal.value.open 
        && !(
            awardsModal.value.contains(event.target) || 
            postId
        )
    ) {
        awardsModal.value.close();
        isOpen.value = false;
        postId = null;
    }
}

// Make a watcher for an event listener when someone clicks outside the dialog. 
watch(
    isOpen, 
    (newValue) => {
        // If there isnt any postmodal data it means you arent clicking on the grant award button
        // otherwise, this callback will automatically close the modal even if you don't want that to happen. 
        if (newValue) {
            document.addEventListener('click', (event) => handleClickOutside(event));
            watch();
        }
    },
);

window.addEventListener('open-award-post-modal', (event) => {
    postId = event.detail.post_id;
    awardsModal.value?.showModal(); 
    isOpen.value = true; 
});

function grantAwardToPost(post, award, useArray) {
    // For ui.
    let awardId = award.id;
    awardStatuses.value[awardId].status === Award.statuses.loading
    if (!post) return;
    if (!useArray) return;

    // This assumes the count is always 0.
    // use array, 0 index is current Uses, 1 index is allowed uses.
    // early out if you are already at the limit of the awards allotted uses.
    if (awardStatuses.value[awardId].grantable && useArray[0] >= useArray[1]) return;

    db.put(urls.bookclubs.grantAwardToPost(bookclub, post.id, awardId), null, false, 
        (res) => {
            // this is where you should see whether the award can still be granted or not by incrementing the count of grants a particular award has been given.
            // TODO: Update this so that it works.
            // awardStatuses.value[awardId].status === Award.statuses.loading
            loading.value = false;
            award.current_uses += 1;
            let channel = `award-granted-to-${postId}`;
            console.log(channel, award, 'before pubsub')
            PubSub.publish(channel, { award });
        },
        (err) => {
            console.log(err)
            loading.value = false;
        }
    );
};


function ungrantAwardFromPost(post, award) {
    db.delete(urls.bookclubs.ungrantAwardToPost(route.params.bookclub, post.id, award.id), 
    null, 
    false, 
    (res) => {
        award.current_uses -= 1;
    }, 
    (err) => {
        console.log(err);
    });
}
</script>
<style scoped>
.h-40 {
    height: 40px;
}

.transition {
    transition: all 150ms ease-in-out;
}

@starting-style {
    .awards-menu {
        opacity: 0;
        height: 0;
        right: -9999px;
    }
}

.awards-menu[open] {
    --mobile-sidebar-width: 90vw;
    @media screen and (min-width: 768px) {
        --mobile-sidebar-width: 700px;
    }

    transition-behavior: allow-discrete;
    transition: 300ms ease;
    width: var(--mobile-sidebar-width);
    height: 80vh;
    scroll-behavior: smooth;
    overflow-y: scroll;
    min-width: 300px; /** For mobile */
    border: 1px solid var(--stone-200);
    border-radius: var(--radius-md);
    margin-left: auto;
    margin-right: auto;
    margin-top: 60px;
    padding: 24px;
    padding-top: 0;
    background-color: var(--surface-primary);
}

.awards-menu::backdrop {
  display:none
}

.award-grid {
    align-items: start;
    text-align: center;
    margin-top: 20px;
}

.award-type {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    justify-content: space-around;
    width: 100%;
    overflow-x: scroll;
    column-gap: 20px;
    row-gap: 20px;
}

.award {
    padding: 4px;
    padding-bottom: 8px;
    border-radius: 8px;
    transition: all 250ms ease;
    outline-offset: 4px;
    margin-bottom: 5px;

    &:hover {
        background-color: var(--stone-300);

        .award-front {
            box-shadow: rgba(0, 0, 0, 0.06) 0px 2px 4px 0px inset;
        }
    }

    &:active {
        background-color: var(--stone-400);
    }

    .award-front {
        display: block;
        padding: 4px 12px;
        border-radius: 8px;
        font-size: 1.25rem;
        background: var(--stone-50);
        color: white;
        transform: translateY(-5px); 

        &:active {
            transform: translateY(-2px);
            background-color: var(--indigo-50);
            box-shadow: rgba(0, 0, 0, 0.1) 0px 2px 4px 0px inset;
        }
    }

    .award-icon {
        margin-left: auto;
        margin-right: auto;
        height: 80px;
        width: 80px;
        color: var(--text-indigo-500);
        fill: var(--text-indigo-500);
    }

    .award-title {
        font-family: var(--fancy-script);
        font-size: var(--font-lg);
        color: var(--indigo-600);
    }

    .award-description {
        font-size: var(--font-sm);
        color: var(--stone-600)
    }

    .loading {
        pointer-events: none;
        filter: blur(10px)
    }

    /* &.expired {
        background-color: var(--stone-50);
        color: var(--stone-400);
    }

    &.granted:not(&.expired) {
        background-color: var(--indigo-200);
        border-color: var(--indigo-400);
    } */
}
</style>