<template>
    <label :for="props.inputId">
        <p class="text-sm text-slate-600 mb-2">{{ props.name }}</p>
        <div class="flex gap-5">
            <input
                :type="props.inputType"
                id="user-name"
                class="settings-info-form-input"
                v-model="data"
            >

            <button
                v-if="!showSaveField"
                type="button"
                class="edit-btn filled border"
                @click="showSaveField = true"
            >
                <IconEdit/>  
            </button>
            <button
                v-if="showSaveField"
                type="button"
                class="save-btn"
                :class="{'disabled': props.isSaveDisabled}"
                :disabled="props.isSaveDisabled"
                @click="emit('new-value-saved', data)"
            >
                Save  
            </button>
            <button
                v-if="showSaveField"
                type="button"
                class="cancel-btn"
                @click="showSaveField = false"
            >
                Cancel  
            </button>
        </div>
    </label>    
</template>
<script setup>
import IconEdit from '../../svg/icon-edit.vue';
import { ref, watchEffect } from 'vue';

const props = defineProps({
    name: {
        type: String,
        required: true,
    },
    value: {
        type: String,
    },
    inputId: {
        type: String,
    },
    inputType: {
       type: String,
       required: true
    },
    isSaveDisabled: {
        type: Boolean,
        default: false,
    },
})

const emit = defineEmits(['new-value-saved']);

const showSaveField = ref(false);
const data = ref(props.value)

watchEffect(() => {
    emit('updated:string', data.value)
})
</script>