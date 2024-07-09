<template>
    <ul class="container questions" :class="{'mt-10': !isComparison}">
        <li v-for="(question, i) in questions" :key="i">
            <div class="my-3 text-lg question-border px-5 py-5 w-100 box-btn justify-between items-center"
                :class="{'error': question.error}"
            >
                <div class="text-start">
                    <!-- If we are looking at a custom review type question. -->
                    <span v-if="!props.isComparison && question.id < 0" class="block fancy">Your response</span>

                    <!-- If we are looking at regular review type templated questions -->
                    <span v-if="!props.isComparison && question.id >= 0" class="block">{{ question.q }}?</span>
                    <!-- Either way both share this response form. -->
                    <span v-if="!props.isComparison" class="block text-slate-400 text-start" :key="question.response">
                        {{ question.response }}
                    </span>

                    <!-- If we are looking at comparison type questions -->
                    <span v-if="props.isComparison" class="block">{{ `The ${question.topic} of both books...` }}</span>
                    <span v-if="props.isComparison" class="block text-slate-400 text-start">{{ question.comparison || question.response }}</span>
                </div>
            </div>
            <div v-if="question.error" class="text-start text-red-500 text-sm">{{ question.error }}</div> 
        </li>
    </ul>

    <div v-if="!questions.length" style="text-align: center;" :class="{'mt-10 mb-10': isComparison}">
        <h2 class="heading">You haven't added any responses</h2>

        <p class="subheading">Click 
            <button type="button" 
                class="underline text-indigo-500"
                @click="emit('go-to-edit-section')"    
            >here</button> to add some responses
        </p>
    </div>
</template>
<script setup>
import { reactive, computed, watch } from 'vue';
import { createQuestionStore } from '../../../stores/createPostStore';
import CreatePostResponseForm from './createPostResponseForm.vue';
import IconChevron from '../../svg/icon-chevron.vue';

const props = defineProps({
    isViewingReview: {
        type: Boolean,
        required: true,
    },
    questions: {
        type: Array,
        required: false,
    },
    isComparison: {
        type: Boolean,
        required: false,
        default: false,
    },
});

const store = createQuestionStore();
const questions = computed(() => { 
    if (props.questions?.length) {
        return props.questions;
    } else if (store.arr) {
        return store.arr;
    } else { 
       return [];
    }
});

const createPostResponseFormDict = reactive({});

const emit = defineEmits(['question-form-completed', 'go-to-edit-section']);

function storeChangeHandler(indexOfQ) {
    // take the current question and close the response form once you add it!
    createPostResponseFormDict[indexOfQ] = !createPostResponseFormDict[indexOfQ];
    emit('question-form-completed');
};

watch(questions, (newValue) => {
    /**  
    * Grab the index of the newest question that was added to yourReviewQuestions
    * and set a value to the dictionary of `false` so you can open and close
    */
    const index = questions.value.indexOf(newValue);
    createPostResponseFormDict[index] = false;
});
</script>
<style scoped>
.justify-between {
    display: flex;
    justify-content: space-between;
    padding-top: .5rem;
    padding-bottom: .5rem;
}

.box-btn-remove {
    color: #e11d48;
    width: 24px;
    height: 24px;
}

.btn-expand {
    padding: 4px;
    background-color: var(--indigo-200);
    border-radius: var(--radius-sm);
    transition-duration: var(--transition-short);
    cursor: pointer;
}

.btn-expand.expanded {
    transform: rotate(180deg);
    background-color: var(--indigo-100);
}

</style>