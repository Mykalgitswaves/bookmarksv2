<template>
    <div>
        <p v-if="$slots.helpText" class="display-block text-sm text-stone-600">
            <slot name="helpText"></slot>
        </p>
        
        <input 
            type="date"
            class="date-picker" 
            v-model="date"
        />
    </div>
</template>
<script setup>
import {ref, watchEffect, } from 'vue';

const date = ref(new Date());
const emit = defineEmits('model-value-updated')

watchEffect(() => {
    emit('model-value-updated', date.value)
});
</script>
<style scoped>
.date-picker {
    padding: 8px 12px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--indigo-300); 
    margin-top: 10px;
    font-family: var(--fancy-script);
    color: var(--indigo-400);

    &::popover {
        border: 1px solid var(--stone-500);
        border-radius: var(--radius-sm);
        box-shadow: var(--shadow-lg);
    }
    
}
</style>
