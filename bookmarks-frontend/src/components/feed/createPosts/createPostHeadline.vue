<template>
    <div class>
        <p class="text-2xl font-medium my-5 text-slate-600">Add a headline (TLDR) for your review.</p>
        
        <label 
            for="headline"
            class="block text-indigo-400 my-2"
        >This will appear front and center on your review</label>

        <input 
            id="headline" 
            type="text"
            placeholder="A masterpiece - someguy"
            class="border-indigo-500 border-solid border-2 rounded-md px-2 py-1 w-60"
            v-model="headline"
        >
    </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const headline = ref('')
const emit = defineEmits();

watch(headline, () => {
    emit('headline-changed', headline.value);
});

</script>