<template>
    <div class>
        <p class="mb-2 mt-5 text-stone-600">Add a headline for your {{ props.reviewType }}.</p>
        
        <label 
            for="headline"
        >
            <input 
                id="headline" 
                type="text"
                placeholder="A masterpiece - someguy"
                class="border-indigo-200 border-2 rounded-md px-2 py-2 w-100"
                :class="{'max-w-[600px] border-solid': !reviewVersion, 'review-search-bar': reviewVersion}"
                v-model="headline"
                :maxlength="SMALL_TEXT_LENGTH"
            >
            <span v-if="!headlineError" class="block text-gray-600 text-sm my-2">This will appear front and center on your {{ props.reviewType }}</span>
            <span v-if="headlineError" class="block text-red-500 text-sm my-2"> {{ headlineError }}</span>
        </label>
    </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { SMALL_TEXT_LENGTH } from '../../../services/forms'
const props = defineProps({
    headlineError: {
        type: String,
        required: false,
    },
    propHeadline: {
        type: String,
        required: false,
    },
    reviewType: {
        type: String,
        required: false,
        default: () => ('review'),
    },
    reviewVersion: {
        type: Boolean,
        default: false,
    }
});
const headline = ref('')

if(props.propHeadline){
    headline.value = props.propHeadline;
}

const emit = defineEmits();

watch(headline, () => {
    emit('headline-changed', headline.value);
});
</script>
<style scoped>
.review-search-bar {
    font-family: var(--fancy-script);
    border-style: dashed;
}
</style>