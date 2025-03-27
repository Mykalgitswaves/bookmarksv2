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
                v-if="!club.currently_reading_book?.is_user_finished_reading"
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
import IconPlus from '@/components/svg/icon-plus.vue';
import ViewAwards from './awards/ViewAwards.vue'
// Used to show and hide modals.

const props = defineProps({
    club: {
        type: Object,
        required: true,
    },
});

const emit = defineEmits(['start-club-update-post-flow']);
</script>
<style scoped>
.sticky-top {
    position: sticky;
    top: 0;
    left: 0;
}
</style>