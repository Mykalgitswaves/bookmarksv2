<template>
    <ul class="container questions">
        <li v-for="(question, i) in questions" :key="i">
            <div class="my-3 text-lg question-border px-5 py-5 cursor-pointer w-100 box-btn justify-between">
                <button type="button"
                    class="text-start"
                    @click="createPostResponseFormArr[i] = !createPostResponseFormArr[i]"
                    :ref="(el) => createPostResponseFormArr.push(el)"
                >
                        <span v-if="!props.isComparison" class="block">{{ question.q }}?</span>
                        <span v-if="!props.isComparison" class="block text-slate-400 text-start" :key="question.response">
                            {{ question.response }}
                        </span>

                        <span v-if="props.isComparison" class="block">{{ `The ${question.topic} of both books...` }}</span>

                        <span v-if="props.isComparison" class="block text-slate-400 text-start">{{ question.comparison }}</span>
                </button>
            </div>

            <CreatePostResponseForm 
                v-if="!createPostResponseFormArr[i]" 
                :q="question" 
                :is-comparison="true"  
                :is-viewing-question="true" 
                @store-changed="storeChangeHandler()"
            />
        </li>
    </ul>
    
    
</template>
<script setup>
import { ref, computed, watch } from 'vue';
import { createQuestionStore } from '../../../stores/createPostStore';
import CreatePostResponseForm from './createPostResponseForm.vue';
import IconRemove from '../../svg/icon-remove.vue';

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
    }
});

const store = createQuestionStore();

const questions = computed(() => { 
    if (props.questions.length) {
        return props.questions;
    } else if (store.arr) {
        return store.arr;
    } else { 
       return [];
    }
});

const createPostResponseFormArr = ref([]);

const emit = defineEmits();

function storeChangeHandler() {
    emit('question-form-completed');
};

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

</style>