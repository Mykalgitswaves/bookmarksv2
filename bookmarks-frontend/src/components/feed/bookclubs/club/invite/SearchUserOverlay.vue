<template>  
    <Button variant="outline" @click="openOverlay()">
        <span class="fancy" style="font-weight: 300">Search user</span>
    </Button>

    <Overlay ref="overlay">
        <template #overlay-header>        
            <SearchForExistingUser  
                :book-club-id="bookClubId"
                @model-value-updated="(users) => populateUserPreviewsFromSearch(users)"
            />
        </template>

        <template #overlay-main>
            <div class="searched-users">
                <div>
                    <div v-for="(user, index) in searchedUsers" :key="index" class="searched-user">
                        <p class="text-lg text-stone-600 fancy mr-auto">
                            {{ user.user_username }}
                        </p>
                    
                        <button 
                            type="button"
                            class="btn btn-ghost btn-tiny" 
                            @click="selectAndCloseModal(user)"
                        >
                            Add invite for user
                        </button>
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
import { Button } from '@/lib/registry/default/ui/button';

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

function selectAndCloseModal(user) {
    emit('user-selected', user); 
    const { dialogRef } = overlay.value;
    dialogRef.close();
}
</script>
<style scoped>
.searched-user {
    display: flex;
    align-items: center;
    margin: 4px;
}
</style>