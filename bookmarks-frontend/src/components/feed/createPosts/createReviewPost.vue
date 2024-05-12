<template>
    <section>
        <BackBtn/>
        <div v-if="!book">
            <p class="text-2xl mb-2 mt-5 font-semibold text-center">The content monster is hungry for your thoughts 🍪. <br/>
                <span class="text-indigo-500">Start by picking a book </span>
            </p>

            <SearchBooks @book-to-parent="bookHandler" :centered="true"/>
        </div>

        <div v-if="book" class="container text-center">
            <div class="my-5">
                <p class="create-post-heading-text">You're reviewing
                    <span class=" create-post-heading-book-title">
                        {{ book.title }}
                    </span>
                </p>
            </div>

            <!-- Progress bar and controls -->
            <div>
                <div class="toolbar">
                    <button type="button"
                        class="toolbar-btn"
                        @click="decrementStep"
                    >Previous</button>

                    <button type="button"
                        class="toolbar-btn"
                        @click="incrementStep"
                    >Next</button>
                </div>


                <p class="text-stone-600 mb-5 mt-2"><span class="text-indigo-500">{{ step }}</span> / 3</p>

                <div class="toolbar-progress">
                    <div class="total" :style="{'width': progressTotal + '%'}"></div>
                    <div class="remaining" :style="{'width': remainderTotal + '%'}"></div>

                    <span class="stepper one" :class="{'active': step >= 1}"></span>
                    <span class="stepper two" :class="{'active': step >= 2}"></span>
                    <span class="stepper three" :class="{'active': step >= 3}"></span>
                </div>
            </div>

            <!-- Setting headlines -->
            <CreatePostHeadline class="mt-15" v-show="step === 1" @headline-changed="headlineHandler" />

            <!-- Adding questions -->
            <div v-show="step === 2">

                <div class="mt-10 mb-10">
                    <h4 class="heading">Click into a topic to add questions to your review.</h4>

                    <p class="subheading">Pick from some pre-made prompts or add your own</p>
                </div>

                <!-- Save some performance by caching stuff -->
                <KeepAlive>
                    <CreateReviewQuestions 
                        :question-map="questionMapping"
                        :is-viewing-review="false"
                        :question-count="count"
                        @question-added="(question) => handleQuestionAdded(question)"
                    />
                </KeepAlive>
            </div>

            <div v-show="step === 3">

                <YourReviewQuestions 
                    :is-viewing-review="true"
                    :is-comparison="false"
                    @question-form-completed="hasQuestionDataHandler()"
                />
            </div>
        </div>
    </section>
</template>
<script setup>
import { ref, defineEmits, watch, computed, reactive } from 'vue'
import { postData } from '../../../../postsData.js';
import { createQuestionStore } from '../../../stores/createPostStore';
import { helpersCtrl } from '../../../services/helpers';
import SearchBooks from './searchBooks.vue';
import CreatePostHeadline from './createPostHeadline.vue';
import CreateReviewQuestions from './createReviewQuestions.vue';
import YourReviewQuestions from './yourReviewQuestions.vue';

// get qs from data and add in entries.
const questionCats = Array.from(Object.keys(postData.posts.review))
console.log(questionCats)
// Refs
const book = ref(null);
const { clone } = helpersCtrl;
const currentTopic = ref('Your post');

// Defaults to character, this change will dictate the questions rendered. we can model it.
// clones of our fixture data.
let characterQuestions = clone(postData.posts.review['character']);
let plotQuestions = clone(postData.posts.review['plot']);
let toneQuestions = clone(postData.posts.review['tone']);
// let allQuestions = clone(postData.posts.review['all']);
let customQuestions = clone(postData.posts.review['custom']);

const store = createQuestionStore();

// refs
const entries = ref([]);
const headline = ref('');
const currentPostTopic = ref('questions')
const step = ref(1);

// used to show certain question sets.
const questionMapping = reactive({
    'custom': customQuestions,
    'character': characterQuestions,
    'plot': plotQuestions,
    'tone': toneQuestions,
    // 'all': allQuestions,
});

const progressTotal = computed(() => Math.floor((step.value * 100) / 3));
const remainderTotal = computed(() => 100 - progressTotal.value);

// functions
const emit = defineEmits(['is-postable-data']);

function hasQuestionDataHandler(){
    entries.value = store.arr
}

function bookHandler(e) {
    book.value = e;
}

function headlineHandler(e) {
    headline.value = e;
}

// emit handlers from child components.
const count = computed(() => {
    return store.arr.length
});

// 
function handleQuestionAdded(question) {
    console.log(question);
}

function incrementStep() {
    if(step.value < 3) {
        step.value += 1;
    }
}

function decrementStep() {
    if(step.value > 1) {
        step.value -= 1;
    }
}

// Add a watcher to emit up when something is added, doesn't seem to capture when entries loses entry with splice so we have duplicate above.
watch(entries, () => {
        emit('is-postable-data', helpersCtrl.formatReviewData(entries.value, book.value, headline.value))
        console.log(entries.value[entries.value.length - 1]);
        // If you added a custom question, add a new one to the end of the reactive list.
        let numOfCustomQuestions = entries.value.filter(q => q.id < 0).length;
        if(numOfCustomQuestions) {
            let lastIdOfCustomQuestionDecremented = entries.value[entries.value.length - 1].id;
            if(lastIdOfCustomQuestionDecremented){
                questionMapping.custom.push({
                    "id": lastIdOfCustomQuestionDecremented - 1,
                    "q": '',
                    "response": '',
                    "is_spoiler": false,
                    "placeholder": "Add your own question here...",
                    "isHiddenCustomQuestion": false
                });
            }
        }
});

watch(headline, () => {
    if(entries.value?.length) {
        emit('is-postable-data', helpersCtrl.formatReviewData(entries.value, book.value, headline.value))
    }
})

watch(currentTopic, () => {
    characterQuestions = JSON.parse(JSON.stringify(postData.posts.review[currentTopic.value]));
})
</script>

<style scoped>

.heading {
    font-size: var(--font-2xl);
    color: var(--stone-700);
    font-weight: 500;
}

.subheading {
    color: var(--stone-600);
}

.text-white { 
    color: #fff;
}

.active {
    border-color: rgb(70, 84, 213);
}

.added {
    background-color: rgb(70, 84, 213) !important;
}

.bg-red-500 {
    background-color: rgb(239 68 68);
}

textarea { 
    width: 100%;
}

.text-start {
    text-align: start;
}

.toolbar {
    display: flex;
    column-gap: 20px;
    justify-content: center;
    align-items: center;
}

.toolbar-btn {
    color: var(--stone-600);
    font-family: var(--fancy-script);
    font-size: var(--font-md);
    padding: 8px 14px;
}

.toolbar-progress {
    width: 100%;
    max-width: 880px;
    position: relative;
    display: flex;
}

.toolbar-progress .total {
    background-color: var(--indigo-500);
    border-bottom: 2px solid var(--indigo-500);
}

.toolbar-progress .remaining {
    background-color: var(--indigo-500);
    border-bottom: 2px solid var(--stone-100);
}

.toolbar-progress .stepper {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background-color: var(--stone-100);
    display: inline-block;
    margin-left: -5px;
    position: absolute;
    top: -5px;
}

.toolbar-progress .stepper.one{
    left: 33%;
}

.toolbar-progress .stepper.two{
    left: 66%;
}

.toolbar-progress .stepper.three{
    right: 0;
}

.stepper.active {
    background-color: var(--indigo-500);
}

.list-move,
.list-enter-active,
.list-leave-active {
  transition: all 0.4s ease;
}
.list-enter-from {
    transition: all 0.5s ease;
    transform: translateY(-10px);
    opacity: 0;
}
.list-leave-to {
  opacity: 0;
}


.box-btn-remove:hover:not([disabled]) {
    color: rgb(220 38 38);
}

.max-h-50 {
    max-height: 50px;
}

.border-indigo-500 {
    border: solid 2px var(--indigo-500);
}
.active {
    background-color: var(--indigo-500);
    color: #fff;
    border-color: var(--indigo-500);
}
</style>