<template>
    <div class="flex justify-between pt-5 pb-5 sticky-top">
        <div class="flex items-center">
            <button 
                class="btn btn-ghost btn-icon btn-tiny text-sm fancy"
                type="button"
                @click="emit('start-club-update-post-flow')"
            >
                <IconPlus/> 
                Update
            </button>

            <button 
                v-if="!statusForClub.userFinishedWithCurrentBook"
                class="ml-5 text-sm fancy underline text-stone-500 hover:text-indigo-600"
                type="button"
                @click="emit('finished-reading')"
            >
                I finished reading this book
            </button>

            <h5 v-else class="ml-5 text-sm fancy text-indigo-500">
                ✨🎉 Finished reading 🎉✨
            </h5>
        </div>

        <ViewAwards/>
    </div>
</template>
<script setup>
import { computed } from 'vue';
import IconPlus from '@/components/svg/icon-plus.vue';
import ViewAwards from './awards/ViewAwards.vue'

import { useCurrentUserStore } from '@/stores/currentUser';
// Used to show and hide modals.

const props = defineProps({
    club: {
        type: Object,
        required: true,
    },
});

const emit = defineEmits(['start-club-update-post-flow']);

const store = useCurrentUserStore();
const { user } = store;

const statusForClub = computed(() => {
    const status = user.clubs[props.club.book_club_id];
    if (!status) {
        console.warn('something weirds afoot with status @ BookClubFeedActions')
        return false
    }
    return status;
});
</script>
<style scoped>
.sticky-top {
    position: sticky;
    top: 0;
    left: 0;
}
</style>