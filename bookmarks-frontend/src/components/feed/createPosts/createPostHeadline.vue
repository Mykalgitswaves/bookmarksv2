<template>
    <div class>
        <p class="text-2xl font-medium mb-2 mt-5 text-slate-600">Add a headline (TLDR) for your {{ props.reviewType }}.</p>
        
        <label 
            for="headline"
        >
            <input 
                id="headline" 
                type="text"
                placeholder="A masterpiece - someguy"
                class="border-indigo-200 border-solid border-2 rounded-md px-2 py-2 w-100 max-w-[600px]"
                v-model="headline"
            >
            <span class="block text-gray-600 text-sm my-2">This will appear front and center on your {{ props.reviewType }}</span>
        </label>
    </div>
</template>

<script setup>
import { ref, watch } from 'vue'
const props = defineProps({
    reviewType: {
        type: String,
        required: false,
        default: () => ('review'),
    },
})
const headline = ref('')
const emit = defineEmits();

watch(headline, () => {
    emit('headline-changed', headline.value);
});

</script>