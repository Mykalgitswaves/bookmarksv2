<template>
    <YourReviewQuestions 
        :questions="store.arr"
        :is-comparison="true"
        :is-viewing-review="true" 
        @go-to-edit-section="emit('go-to-edit-section')" 
    />
</template>
<script setup>
import { watch } from 'vue';
import { createQuestionStore } from '../../../../stores/createPostStore';
import YourReviewQuestions from '../yourReviewQuestions.vue';

const emit = defineEmits(['go-to-edit-section']);
const store = createQuestionStore();

</script>