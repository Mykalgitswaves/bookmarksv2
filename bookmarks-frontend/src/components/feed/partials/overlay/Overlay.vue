<template>
    <dialog ref="dialogRef" class="overlay">
            <div class="controls">
                <!-- just in case you need special shit up top -->
                <slot name="overlay-controls-header"></slot>

                <button 
                    type="button" 
                    class="btn btn-tiny text-stone-600"
                    role="navigation"
                    @click="dialogRef.close(); emit('closed-modal')"    
                >
                    <IconExit />
                </button>
            </div>

            <slot name="overlay-header" class="overlay-header"></slot>

            <slot name="overlay-main" class="overlay-main"></slot>

            <slot name="overlay-footer" class="overlay-footer"></slot>
    </dialog>
</template>
<script setup>
import { ref, defineExpose } from 'vue';
import IconExit from '@/components/svg/icon-exit.vue'

const dialogRef = ref(null);
const emit = defineEmits(['closed-modal']);

defineExpose({
    dialogRef
});
</script>
<style scoped>
.overlay {
    height: fit-content;
    padding: 8px 14px;
    border-radius: 14px; 
    background-color: var(--surface-primary);
    box-shadow: var(--shadow-lg);
    min-height: 280px;
    border: none;
    overflow-y: scroll;

    .controls {
        display: flex;
        justify-content: end;
    }
}
</style>