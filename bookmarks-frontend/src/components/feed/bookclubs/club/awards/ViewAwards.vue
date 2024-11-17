<template>
<button 
    ref="awardsButton"
    class="btn btn-ghost btn-tiny text-sm btn-icon"
    @click="showOrHideAwardsDialog()"    
>
    Awards
</button>

<dialog ref="awardsModal" class="awards-menu">
    <div class="pt-5 pb-5">
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
                <div class="toolbar">
                    <button 
                        v-if="postId" 
                        class="btn btn-toolbar text-sm active"
                    >
                        post awards
                    </button>
                    
                    <button class="btn btn-toolbar text-sm"
                    >
                        club awards
                    </button>
                </div>

                <div class="award-grid">
                    <div v-for="(category, key) in awards" 
                        :key="index"
                    >
                        <h3 class="text-xl text-stone-700 fancy text-start mb-5 mt-5">
                            {{ key }}
                        </h3>

                        <div class="award-type" v-if="category">
                            <div v-for="award in category" 
                                :key="award.id" 
                            >
                                <div 
                                    class="award"
                                    :class="{
                                        'granted': awardStatuses[award.id].status === Award.statuses.grantable,
                                        'expired': awardStatuses[award.id].status === Award.statuses.expired,
                                        'loading': awardStatuses[award.id].status === Award.statuses.loading,
                                    }"
                                    @click="grantAwardToPost(postId, award.id, [award.current_uses, award.allowed_uses])"
                                >
                                    <span class="award-front">    
                                        <p class="award-title">{{ award.name }}</p>
                                        <p class="award-description">{{  award.description }}</p>
                                    </span>
                                </div>
                                
                                <p class="text-xs bold text-stone-500 text-center">{{ `${award.current_uses} granted on this post, ${award.allowed_uses - award.current_uses} remaining` }}</p>

                                <button 
                                    v-if="award.current_uses > 0"
                                    type="button" 
                                    class="mt-5 text-xs text-red-500 " 
                                    @click="removeAwardFromPost(postId, award.id)"
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

        // this is marginally faster than a normal for loop.
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

            index += 1
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

const awardsButton = ref(null);
const awardsModal = ref(null);
const isOpen = ref(false);

/**
 * @UI_functions
 */
function showOrHideAwardsDialog() {
    if (awardsModal.value) {
        if (!awardsModal.value.open) { 
            awardsModal.value.showModal(); 
            isOpen.value = true; 
        } else {
            awardsModal.value.close();
            isOpen.value = false;
            postId = null;
        } 
    }
}


function handleClickOutside(event){
    if (
        awardsModal.value 
        && awardsModal.value.open 
        && !(
            awardsModal.value.contains(event.target) || 
            awardsButton.value.contains(event.target) || 
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

function grantAwardToPost(postId, awardId, useArray) {
    // For ui.
    awardStatuses.value[awardId].status === Award.statuses.loading
    if (!postId) return;
    if (!useArray) return;

    // This assumes the count is always 0.
    // use array, 0 index is current Uses, 1 index is allowed uses.
    // early out if you are already at the limit of the awards allotted uses.
    if (awardStatuses.value[awardId].grantable && useArray[0] >= useArray[1]) return;

    db.put(urls.bookclubs.grantAwardToPost(bookclub, postId, awardId), null, false, 
        (res) => {
            // this is where you should see whether the award can still be granted or not by incrementing the count of grants a particular award has been given.
            // TODO: Update this so that it works.
            // awardStatuses.value[awardId].status === Award.statuses.loading
            loading.value = false;
        },
        (err) => {
            console.log(err)
            loading.value = false;
        }
    );
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
    background-color: var(--stone-400);
    padding: 4px;
    padding-bottom: 8px;
    border-radius: 4px;
    transition: all 250ms ease;
    outline-offset: 4px;
    border-radius: 12px;

    .award-front {
        display: block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 1.25rem;
        background: var(--stone-50);
        color: white;
        transform: translateY(-5px); 

        &:active {
            transform: translateY(-2px);
        }
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