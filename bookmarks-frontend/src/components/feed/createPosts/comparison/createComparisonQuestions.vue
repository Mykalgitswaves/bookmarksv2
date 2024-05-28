<template>
<ul v-if="initialized">
    <li v-for="([questionType, questions], index) in qset"
        :key="index"
        :ref="(el) => activeQuestionCat.push(el)"
    >
        <button
            :class="{'has-questions': questions.find((q) => q.response?.length > 0)}"
            class="question-topic"
            type="button"
            @click="activeQuestionCat[index] = !activeQuestionCat[index]"
        >
            <Component :is="categoryIconMapping[questionType]" class="question-topic-icon"/>
            <span class="fancy">{{ questionType === 'custom' ? 'Add your own thoughts' : ToTitleCase(questionType) }}</span>

            <IconChevron :class="{'active-chevron': activeQuestionCat[index]}"/>
        </button>

        <!-- Subsection of a particular category -->
        <Transition name="content" tag="div">
            <ul  v-if="questionType === 'custom' ? activeQuestionCat[index] : !activeQuestionCat[index]" class="container questions">
                <li v-for="(question, i) in questions" 
                    :key="question.id"
                    class="mb-5"
                >   
                    <div v-if="question"
                        class="my-2 text-lg question-border px-5 py-5 cursor-pointer w-100 box-btn"
                        :class="{'active': state.has(question.id)}"
                    >
                        <form class="text-start w-100">
                            <span v-if="question.id >= 0" class="block">{{ question?.q }}?</span>
                        
                            <textarea name="response" type="text" 
                                :style="{ height: debouncedGenQuestionHeight(question.id) + 'px' }"
                                :id="question.id"
                                class="create-question-response" 
                                v-model="question.response"
                                ref="textarea"
                                :placeholder="question.id >= 0 ? 'type your response here...' : 'Add your own thoughts here...'"
                                @keyup="debouncedAddQuestionToStore(question)"
                            />
                        </form>
                    </div>

                    <div v-if="state.has(question.id)" class="flex justify-between items-center w-100">
                        <p class="text-start text-indigo-400 text-sm">
                            Question added
                        </p>
                        
                        <button 
                            type="button"
                            class="text-red-600 w-20 box-btn-remove"
                            @click="removeQuestionFromStore(question)"
                        >
                            <IconRemove style="height: 12px; width: 12px; fill: var(--red-400);" />
                            Remove
                        </button>
                    </div>

                    <!-- FOr custom questions you might want to add. -->
                    <button v-if="(question.topic === 'custom') && (i === questions.length - 1)"
                        type="button"
                        class="btn btn-ghost btn-icon mt-2" 
                        @click="addCustomQuestion()">
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
import { ref, onUnmounted, reactive, onMounted, computed, watch } from 'vue';
import { helpersCtrl, ToTitleCase } from '../../../../services/helpers';
import { Comparison, formatQuestionStoreForPost, initialize, customQuestion, resetQuestions } from './comparison';
import { createQuestionStore } from '../../../../stores/createPostStore';
import IconChevron from '../../../svg/icon-chevron.vue';
import IconRemove from '../../../svg/icon-remove.vue';
import IconPlus from '../../../svg/icon-plus.vue';
import { categoryIconMapping } from '../../createPosts/questionCategories.js';

const props = defineProps({
    books: {
        type: Array,
        required: true
    },
    headlines: {
        type: Array,
        required: false,
    },
});

const store = createQuestionStore();
const { state } = store;
const emit = defineEmits(['postable-store-data', 'question-added']);
const questionMapping = reactive({});
const activeQuestionCat = ref([]);
const initialized = ref(false);
const qset = computed(() => Object.entries(questionMapping));
const { debounce } = helpersCtrl;

onMounted(() => {
    initialize(questionMapping)
    initialized.value = true;
});

onUnmounted(() => {
    // this function resets the value of questionMapping
    questionMapping.value = {};
    resetQuestions(questionMapping);
});

function addCustomQuestion() {
    Comparison.createBlankQuestion(customQuestion);
    questionMapping.custom = Comparison.getQuestionsByTopic('custom');
}

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
}

function generateQuestionHeightWithCache(id) {   
    textAreaHeight(id);
    return heights.value[id];
}

const debouncedGenQuestionHeight = debounce(generateQuestionHeightWithCache, 200, true);

function addQuestionToStoreFn(question) {
    if(state.has(question)){
        store.addOrUpdateQuestion(question);
    } else {
        question.topic;
        question.book_ids = [ props.books[0].id, props.books[1].id ];
        question.comparator_id = question.id;
        question.small_img_url = [ props.books[0].small_img_url, props.books[1].small_img_url ]
        question.comparator_a_title = props.books[0].title;
        question.comparator_b_title = props.books[1].title;
        console.log(question)
        store.addOrUpdateQuestion(question);
    }
        const postData = formatQuestionStoreForPost(store.arr, props.headlines);

        emit('postable-store-data', postData)
        emit('question-added');
};

const debouncedAddQuestionToStore = debounce(addQuestionToStoreFn, 200, true);

function removeQuestionFromStore(question){
    if(question.topic === 'custom' && question.id !== -1){
        let index = questionMapping.custom.indexOf(question)
        questionMapping.custom.splice(index, 1);
    }

    question.response = '';
    store.deleteQuestion(question)
};

watch(props.headlines, () => {
    const postData = formatQuestionStoreForPost(store.arr, props.headlines);
    emit('postable-store-data', postData);
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