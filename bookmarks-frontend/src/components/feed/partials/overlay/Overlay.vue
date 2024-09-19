<template>
    <teleport to="body" tag="div">
        <div class="overlay">
            <div class="controls">
                <!-- just in case you need special shit up top -->
                <slot name="overlay-controls-header"></slot>

                <button 
                    type="button" 
                    class="btn btn-tiny text-stone-600"
                    role="navigation"
                    @click="$emit('close-overlay')"    
                >
                    <IconExit />
                </button>
            </div>

            <slot name="overlay-header" class="overlay-header"></slot>

            <slot name="overlay-main" class="overlay-main"></slot>

            <slot name="overlay-footer" class="overlay-footer"></slot>
        </div>
    </teleport>
</template>
<script setup>
import IconExit from '@/components/svg/icon-exit.vue'
</script>
<style scoped>
.overlay {
    display: block;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    max-width: 768px;
    min-width: 60vw;
    padding: 8px 14px;
    border-radius: 14px; 
    background-color: var(--surface-primary);
    box-shadow: var(--shadow-lg);
    min-height: 280px;

    .controls {
        display: flex;
        justify-content: end;
    }
}
</style>