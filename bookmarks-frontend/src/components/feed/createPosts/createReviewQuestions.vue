<template>
    <!-- This represents a list of questions and corresponding categories for each. -->
    <ul>
        <li v-for="(questionType, index) in qset"
            :key="index"
            :ref="(el) => activeQuestionCat.push(el)"
        >
            <button
                :class="{'has-questions': questionType[1].find((q) => q.response.length > 0)}"
                class="question-topic"
                type="button"
                @click="activeQuestionCat[index] = !activeQuestionCat[index]"
            >
                <Component :is="categoryIconMapping[questionType[0]]" class="question-topic-icon"/>
                <span class="fancy">{{ questionType[0] === 'custom' ? 'Add your own thoughts' : ToTitleCase(questionType[0]) }}</span>

                <IconChevron :class="{'active-chevron': activeQuestionCat[index]}"/>
            </button>

            <!-- Subsection of a particular category -->
            <Transition name="content" tag="div">
                <ul  v-if="questionType[0] === 'custom' ? activeQuestionCat[index] : !activeQuestionCat[index]" 
                    class="container questions"
                >
                    <li v-for="(question, i) in questionType[1]" 
                        :key="i"
                        class="mb-5"
                    >   
                        <div v-if="question && (question?.id >= 0 || !question?.isHiddenCustomQuestion)"
                            class="my-2 text-lg question-border px-5 py-5 cursor-pointer w-100 box-btn"
                            :class="{'active': state.has(question.id)}"
                        >
                            <form class="text-start w-100">
                                <span v-if="question.id >= 0" class="block">{{ question?.q }}?</span>
                                
                                <!-- <span v-else class="block">{{ question?.placeholder }}</span> -->
                            
                                <textarea 
                                    name="response" 
                                    type="text" 
                                    :style="{ 'height': heights[question.id] + 'px' }"
                                    :id="question.id"
                                    class="create-question-response" 
                                    v-model="question.response"
                                    ref="textarea"
                                    :maxlength="LARGE_TEXT_LENGTH"
                                    :placeholder="question.id >= 0 ? 'type your response here...' : 'Add your own thoughts here...'"
                                    @keyup="debouncedUpdateQuestion(question); throttledGenQuestionHeight(question.id)"
                                />
                            </form>
                        </div>

                        <div v-if="state.has(question.id)" class="flex justify-between items-center w-100">
                            <p class="text-start text-indigo-400 text-sm">
                                Question added
                            </p>
                            
                            <button type="button"
                                class="text-red-600 w-20 box-btn-remove"
                                @click="removeQuestionFromStore(question)"
                            >
                                <IconRemove style="height: 12px; width: 12px; fill: var(--red-400);" />
                                Remove
                            </button>
                        </div>
                        <!-- FOr custom questions you might want to add. -->
                        <button v-if="(question.id < 0) && (i === questionType[1].length - 1)"
                            type="button"
                            class="btn btn-ghost btn-icon mt-2" 
                            @click="$emit('custom-question-added', question)">
                            <IconPlus />    

                            Add another response
                        </button>
                    </li>
                </ul>
            </Transition>
        </li>
    </ul>
</template>
<script setup>
import { ref, watch, computed } from 'vue';
import { helpersCtrl, throttle, ToTitleCase } from '../../../services/helpers';
import { createQuestionStore } from '../../../stores/createPostStore';
import IconChevron from '../../svg/icon-chevron.vue';
import IconRemove from '../../svg/icon-remove.vue';
import IconPlus from '../../svg/icon-plus.vue';
import { categoryIconMapping } from '../createPosts/questionCategories.js';
import { LARGE_TEXT_LENGTH } from '../../../services/forms'

const props = defineProps({
    questionMap: {
        type: Object,
        required: true,
    },
    isViewingReview: {
        type: Boolean,
        required: false,
    },
    questionCount: {
        type: Number,
    }
});

const { clone, debounce } = helpersCtrl;

const store = createQuestionStore();

const textarea = ref([]);
const heights = ref({});
const cachedQuestions = {};

function textAreaHeight(id) {
    let question;
    // Only loops through our questions once. saves some performance.
    if (cachedQuestions[id]) {
        question = cachedQuestions[id];
    } else {
       question = textarea.value.find((question) => parseInt(question.id, 10) === parseInt(id, 10));
       cachedQuestions[id] = question;
    }
    
    if (question) {
        heights.value[id] = parseInt(question?.scrollHeight, 10);
    } else {
        heights.value[id] = 30;
    }

    console.log(heights.value[id], 'from inside textAreaHeight fn');
    console.log(id, 'from inside textAreaHeight fn');
}

function generateQuestionHeightWithCache(id) {   
    textAreaHeight(id);
    return heights.value[id];
}

const throttledGenQuestionHeight = throttle(generateQuestionHeightWithCache, 100);

const { state } = store;

const qset = computed(() => {
    return Array.from(Object.entries(props.questionMap));
});

const isCurrentQuestionAdded = (question) => { 
    state.has(question.id);
};

const activeQuestionCat = ref([]);

activeQuestionCat.value.forEach((boolean) => (boolean.value = false));

function updateQuestion(question) {
    if(!question.response.length){
        return;
    }
    // console.log(question, 'from inside update question fn');
    store.addOrUpdateQuestion(question);
    // Maybe add more logic in here to emit the shit.
    emit('question-updated');
}

const debouncedUpdateQuestion = debounce(updateQuestion, 200, false);

const emit = defineEmits(['question-added', 'deleted-custom-question', 'question-updated']);

function removeQuestionFromStore(question){
    question.response = '';
    store.deleteQuestion(question)
    emit('deleted-custom-question', question);
}

watch(() => props.questionCount, (newValue) => {
    emit('question-added', newValue);
});
</script>
<style scoped>

.create-question-response {
    width: 100%;
    border: none;
    appearance: none;
    resize: none;
    color: var(--stone-600);
    margin-right: 4px;
    padding-top: 8px;
    background-color: transparent
}

.create-question-response:focus {
    border: none;
    outline: none;
}

.active-chevron {
    transform: rotate(180deg);
}

.questions .box-btn {
    width: 100%;
    padding: 1ch;
    line-height: 1.2;
    display: flex;
    justify-content: space-between;
    align-items: center;
}


.box-btn-remove {
    display: flex;
    column-gap: 4px;
    align-items: center;
    width: fit-content;
    color: var(--red-400);
    font-size: var(--font-sm);
    transition-duration: 250ms;
    transition-timing-function: ease;
}

.box-btn-remove:hover {
    color: var(--red-500);
}

.add-question {
    color: #818cf8;
}
</style>