<template>
    <label :for="name" class="generic-text-area">
        <p class="text-sm text-stone-500 fancy mb-2">
            <slot name="labelAbove"></slot>
        </p>
        <textarea 
            v-model="vModelRef" 
            :name="name" 
            :id="name" 
            :style="{
                'max-width': maxWidth || 'none', 
                'min-height': minHeight || 'none',
            }" 
            @input="emit('updated:modelValue', vModelRef)"
        />
    </label>
</template>
<script setup>
import { ref } from 'vue';

const props = defineProps({
    name: {
        type: String,
        required: true,
    },
    maxWidth: {
        type: String,
        required: false
    },
    minHeight: {
        type: String,
        required: false,
    },
    vModel: {
        type: [String, Boolean],
        required: true,
        default: ''
    }
});

const emit = defineEmits(['updated:modelValue']);
const vModelRef = ref(props.vModel ?? '');

</script>
<style scoped>
.generic-text-area {

}

.generic-text-area textarea {
    border: 1px solid var(--stone-300);
    border-radius: 4px;
    padding: 8px 4px;
    resize: none;
    height: auto;
    font-size: var(--font-sm);
    width: 100%;
}
</style>