<template>
<label :for="inputName">
    <span class="pl-2 pb-1 text-xs text-stone-500 block">
        <slot name="labelAbove"></slot>
    </span>

    <input 
        class="input--2"
        :id="inputName" 
        :placeholder="placeholder" 
        type="text" 
        v-model="vModel" 
        @input="debouncedInputEmit"
    />
    
    <span class="pl-2 pb-1 text-xs text-stone-500 block">
        <slot name="labelBelow"></slot>
    </span>
</label>

</template>
<script setup>
import { ref } from 'vue';
import { helpersCtrl } from '../../../services/helpers';

const props = defineProps({
    inputName: {
        type: String,
        required: true,
    },
    placeholder: {
        type: String,
        required: false,
    }
});

const {debounce} = helpersCtrl;
const vModel = ref('');
const emit = defineEmits(['updated:modelValue'])

function inputEmit() {
    emit('updated:modelValue', vModel.value);
};

const debouncedInputEmit = debounce(inputEmit, 250, false);
</script>
<style scoped>
.input--2 {
    padding: 2px;
    padding-left: 8px;
    border-radius: 4px; 
    border: 1px solid var(--indigo-100);
}

.input--2:active {
    border-color: var(--indigo-300);
}
</style>