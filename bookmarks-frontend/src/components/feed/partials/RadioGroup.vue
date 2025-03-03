<template>
    <!-- dont pass in any html tags here. only regular untagged text -->
    <p v-if="hasHeading" class="text-base text-stone-500">
        <slot name="heading"></slot>
    </p>

    <div class="radio-group">
        <label 
            v-for="(option, index) in options" 
            :key="index" 
            :for="id"
            class="radio"
            @click="emit('updated:modelValue', option.value)"
        >
            <input 
                :name="id"
                :id="`${id}-${option.value}`" 
                type="radio"
                :value="option.value"
                @input="emit('updated:modelValue', option.value)"
            />

            <span class="text-stone-500 text-sm">{{ option.label }}</span>
        </label>
    </div>
</template>
<script setup>
import { ref, useSlots } from 'vue';

const props = defineProps({
    options: {
        type: Array,
        required: true,
    },
    id: {
        type: String,
        required: false,
    }
});

const emit = defineEmits(['updated:modelValue']);
const slots = useSlots();
const heading = slots.heading();
const hasHeading = heading[0]?.children?.length;
</script>
<style scoped>
.radio-group {
    display: flex;
    column-gap: 8px;
    padding: 4px;
}

.radio {
    display: flex; 
    align-items: center;
    column-gap: 4px;
}

.radio[selected] {
    background-color: var(--indigo-300);
}
</style>