<template>  
    <button 
        class="btn btn-tiny w-30 btn-submit"
        type="button" 
        role="navigation"
        @click="isOverlayShowing = true"
    >
        Search for user
    </button>

    <Overlay 
        v-if="isOverlayShowing" 
        @close-overlay="isOverlayShowing = false"
    >
        <template #overlay-header>        
            <SearchForExistingUser  
                :book-club-id="bookClubId"
                @model-value:updated="populateUserPreviewsFromSearch"
            />
        </template>
        <template #overlay-main>
            <div class="searched-users">
                <p v-if="!searchedUsers.length">search for a user to add</p>

                <div v-else>
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
</script>
<style scoped></style>