<template>
    <div class="flex justify-between pt-5 pb-5 sticky-top">
        <button 
            class="btn btn-ghost btn-icon btn-tiny text-sm fancy"
            type="button" 
            @click="emit('start-club-update-post-flow')"
        >
            <IconPlus/> 
            Update
        </button>

        <TransitionGroup name="content">
            <button type="button" @click="filterOptionsDialog?.showModal()" class="menu-wrapper">filter feed</button>
            <dialog ref="filterOptionsDialog" class="dropdown">
                <div>
                    hello
                </div>
            </dialog>  
        </TransitionGroup>
    </div>
</template>
<script setup>
import IconPlus from '@/components/svg/icon-plus.vue';
import { ref } from 'vue';

const filterOptionsDialog = ref(null);
const emit = defineEmits(['start-club-update-post-flow']);

</script>