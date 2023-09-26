<template>
    <div class="review-post-wrapper">
        <div></div>
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
        default: () => '',
    },
    id: {
        type: Number,
        required: true
    }
})

const { book, responses, questions, spoilers, username, question_ids, headline, id } = toRefs(props)

</script>
<style scoped>
.review-post-wrapper {
    background: var(--background-container-gradient);
    padding: 1rem;
}
</style>