<template>
    <YourReviewQuestions :questions="store.arr" :is-comparison="true" :is-viewing-review="true"/>
</template>
<script setup>
import { watch } from 'vue';
import { createQuestionStore } from '../../../../stores/createPostStore';
import YourReviewQuestions from '../yourReviewQuestions.vue';

const store = createQuestionStore();

</script>