<template>  
    <button 
        class="btn btn-tiny w-30 btn-submit self-center nowrap"
        type="button" 
        role="navigation"
        @click="openOverlay()"
    >
        Search for an existing user
    </button>

    <Overlay ref="overlay">
        <template #overlay-header>        
            <SearchForExistingUser  
                :book-club-id="bookClubId"
                @model-value:updated="populateUserPreviewsFromSearch"
            />
        </template>
        <template #overlay-main>
            <div class="searched-users">
                <div v-if="searchedUsers.length">
                    <div v-for="(user, index) in searchedUsers" :key="index" class="flex gap-2 p-5 border-2 border-indigo-300">
                        <p>
                            {{ user.user_username }}
                        </p>
                    
                    <button type="button" class="btn btn-ghost" @click="$emit('selected-user', user.user_id)">select</button>
                    </div>
                </div>
            </div>
        </template>
    </Overlay>
</template>
<script setup>
import { ref } from 'vue';
import SearchForExistingUser from './SearchForExistingUser.vue';
import Overlay from '@/components/feed/partials/overlay/Overlay.vue';

defineProps({
    bookClubId: {
        type: String,
        required: true,
    },
});

const emit = defineEmits(['user-selected']);

const overlay = ref(null);


/**
 * @constants
 */

const isOverlayShowing = ref(false);
const searchedUsers = ref([]);
/**
 * @end_of_constants
 */

// This doesnt work.
function populateUserPreviewsFromSearch (users) {
    searchedUsers.value = users;
};

function openOverlay() {
    const { dialogRef } = overlay.value;
    dialogRef.showModal();
}
</script>
<style scoped></style>