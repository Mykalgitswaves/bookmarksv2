<template>
    <label :for="props.inputId">
        <p class="text-sm text-slate-600 mb-2">{{ props.name }}</p>
        <div class="flex gap-5">
            <input v-if="!isTextArea"
                :type="props.inputType"
                class="settings-info-form-input"
                v-model="data"
            >

            <textarea v-if="isTextArea"
                name=""
                id=""
                class="settings-info-form-textarea"
                v-model="data"
            >

            </textarea>

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
                @click="emit('new-value-saved')"
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
    isTextArea: {
        type: Boolean,
        default: false,
    }
})

const emit = defineEmits(['new-value-set', 'new-value-saved']);

const showSaveField = ref(false);
const data = ref(props.value);

watchEffect(() => {
    emit('new-value-set', data.value)
});
</script>