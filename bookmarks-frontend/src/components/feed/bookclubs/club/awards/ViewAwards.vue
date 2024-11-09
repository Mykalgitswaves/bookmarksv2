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
    <div v-if="!postModalData">
        <div class="toolbar">
            <button class="btn btn-toolbar text-sm active">
                club awards
            </button>

            <button class="btn btn-toolbar text-sm">
                awards you've granted
            </button>
        </div>

        <div v-if="loaded" class="award-grid">
            <div
                class="award" 
                v-for="award in awards" 
                :key="award?.id"
            >
                <h4 class="award-title">{{ award.name }}</h4>
                <p class="award-description">{{  award.description }}</p>
            </div>
        </div>
    </div>
    <!-- Otherwise you're looking at a specific post. -->
    <div v-else>

    </div>
</dialog>
</template>
<script setup>
import { urls } from '../../../../../services/urls';
import { db } from '../../../../../services/db';
import { ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import CloseButton from '../../../partials/CloseButton.vue';

let postId;
let awards = {};
let awardsGrantedForPost = {};

const loaded = ref(false);
const route = useRoute();

db.get(urls.bookclubs.getAwards(route.params.bookclub), null, false, (res) => {
    awards = res.awards;
    loaded.value = true;
});

function getAwardsForPost(postId) {
    loaded.value = false;
    db.get(urls.bookclubs.getAwards(route.params.bookclub), 
        { 
            post_id: postId,
            current_uses: true,
        },
        false, 
        (res) => {
            debugger;
            loaded.value = true;
        })
}

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
    getAwardsForPost(postId)
    awardsModal.value?.showModal(); 
    isOpen.value = true; 
});
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
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    justify-content: space-between;
    align-items: start;
    text-align: center;
    margin-top: 20px;
}

.award {
    border: 1px solid var(--stone-200);
    padding: 4px;
    border-radius: 4px;

    .award-title {
        font-family: var(--fancy-script);
        font-size: var(--font-lg);
        color: var(--indigo-600);
    }

    .award-description {
        font-size: var(--font-sm);
    }
}
</style>