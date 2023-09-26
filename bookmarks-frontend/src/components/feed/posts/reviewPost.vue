<template>
    <div class="review-post-wrapper">
        <p class="text-slate-600 text-center">
            <span class="text-indigo-600 cursor-pointer">{{ username }}'s</span>
             review of 
             <span class="block my-2 italic font-semibold">{{ title }}</span>
        </p>
        <p class="fancy text-2xl">{{ headline }}</p>
    </div>   
</template>
<script setup>
import { toRefs } from 'vue'
const props = defineProps({
    book: {
        type: Number,
        required: true,
    },
    title: {
        type: String,
        required: true,
    },
    responses: {
        type: Array,
        required: true,
    },
    questions: {
        type: Array,
        required: true
    },
    spoilers: {
        type: Array,
        required: true,
    },
    username: {
        type: String,
        required: true,
    },
    question_ids: {
        type: Array,
        required: true,
    },
    headline: {
        type: String,
        required: false,
        default: () => 'Not too much thought',
    },
    id: {
        type: Number,
        required: true
    }
})

const { book, responses,
     questions, spoilers,
      username, question_ids,
       headline, id, title } = toRefs(props)

</script>
<style scoped>
.review-post-wrapper {
    background: var(--background-container-gradient);
    padding: 1rem;
    border-radius: .25rem;
    border: solid 2px ;
    margin-block: 1rem;
    /* Fallbacks for non logical prop abiding browsers */
    margin-top: 1rem;
    margin-bottom: 1rem;
}
</style>