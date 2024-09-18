<template>  
    <button 
        class="btn btn-small w-60 btn-submit"
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
                @modelValue:updated="(users) => populateUserPreviewsFromSearch(users)"
            />
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

/**
 * @end_of_constants
 */


function populateUserPreviewsFromSearch (users) {
    console.log(users)
};
</script>
<style scoped></style>