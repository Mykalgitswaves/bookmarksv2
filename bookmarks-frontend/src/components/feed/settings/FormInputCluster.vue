<template>
    <label :for="props.inputId">
        <p class="text-sm text-slate-600 mb-2">{{ props.name }}</p>
        <div class="flex gap-5">
            <input
                type="text"
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
                class="save-btn "
                @click="showSaveField = false"
            >
                Save  
            </button>
        </div>
    </label>    
</template>
<script setup>
import IconEdit from '../../svg/icon-edit.vue';
import { ref, watch } from 'vue';

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
    }
})

const showSaveField = ref(false);
const data = ref('');

// to do add logic for saving here.
watch(() => props.value, (newValue) => {
    console.log(newValue)
})
</script>