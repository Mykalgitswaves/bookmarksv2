<template>
    <div class="flex justify-between pt-5 pb-5 sticky-top">
        <div class="flex">
            <button 
                class="btn btn-ghost btn-icon btn-tiny text-sm fancy"
                type="button" 
                @click="emit('start-club-update-post-flow')"
            >
                <IconPlus/> 
                Update
            </button>
            
            <button
                class="ml-5 text-sm fancy underline text-stone-500 hover:text-indigo-600"
                type="button"
                @click="emit('finished-reading')"
            >
                I finished reading this book
            </button>
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