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

        <div class="flex gap-2">
            <TransitionGroup name="content" tag="div" class="btn-relative">
                <button 
                    ref="show-modal-btn"
                    class="btn btn-ghost btn-tiny text-sm btn-icon"
                    type="button"
                    @click="modals.selectDropdown = !modals.selectDropdown"
                >
                    Filter
                </button>

                <div v-close-modal="{
                    exclude: ['show-modal-btn'],
                    handler: closeModal,
                    args: ['selectDropdown']
                }">
                    <div v-if="modals.selectDropdown"
                        class="popout-flyout shadow-lg filter"
                    >
                        <button 
                            type="button" 
                            v-for="(option, index) in filterOptions"
                            :key="index"
                            @click="currentFilterOptions[option] = true"  
                        >
                            <span class="text-stone-600 text-sm hover:text-stone-700">
                                {{ option }}
                            </span>
                        </button>
                    </div>
                </div>
            </TransitionGroup>
        </div>
    </div>
</template>
<script setup>
import IconPlus from '@/components/svg/icon-plus.vue';
import { watch, reactive } from 'vue';
import ViewAwards from './awards/ViewAwards.vue'
// Used to show and hide modals.
const filterOptions = ['date(newest first)', 'date(oldest first)', 'byUser'];

const modals = reactive({
  selectDropdown: false,
  filterPopout: false,
});

const currentFilterOptions = reactive({})
const emit = defineEmits(['start-club-update-post-flow']);

function closeModal(reactiveKey) {
  modals[reactiveKey] = false;
}

// watch(currentFilterOptions.byUser, () => {
   
// }, { immediate: true });
</script>
<style scoped>
.sticky-top {
    position: sticky;
    top: 0;
    left: 0;
}
</style>