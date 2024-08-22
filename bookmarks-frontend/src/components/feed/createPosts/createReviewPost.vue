<template>
    <section :class="quickReview ? 'p-20' : ''">
        <BackBtn/>
        <div v-if="!book">
            <p class="text-2xl mb-2 mt-5 font-semibold text-center">The content monster is hungry for your thoughts 🍪. <br/>
                <span class="text-indigo-500">Start by picking a book </span>
            </p>

            <SearchBooks @book-to-parent="bookHandler" :centered="true"/>
        </div>

        <div v-if="book" class="container text-center">
            <div class="my-5">
                <p class="create-post-heading-text">
                {{ 
                    quickReview 
                    ? 'You\'ve finished reading ' 
                    : 'You\'re reviewing' 
                }}
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
                    >
                        <span v-if="step < 3">Previous</span>

                        <span v-else>Edit</span>
                    </button>

                    <button type="button"
                        class="toolbar-btn"
                        @click="incrementStep"
                    >
                        <span v-if="step < 2">Next</span>

                        <span v-else>Finalize</span>
                    </button>
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

            <!-- Did you like it buttons -->
            <div v-if="step === 1">
                <ReviewRating @set-rating="(_rating) => setRatingAndIncrementStep(_rating)" />
            </div>

            <!-- Adding questions -->
            <div v-if="step === 2">

                <div class="mt-10 mb-10">
                    <h4 class="heading">
                        Click into a topic to add to your review.
                    </h4>

                    <p class="subheading">Pick from some pre-made prompts or add your own</p>
                </div>

                <!-- Save some performance by caching stuff -->
                <CreateReviewQuestions 
                    :question-map="questionMapping"
                    :is-viewing-review="false"
                    :question-count="count"
                    @question-added="(question) => handleQuestionAdded(question)"
                    @question-updated="throttledUpdateQuestionInEntries()"
                    @custom-question-added="(question) => handleCustomQuestionAdded(question)"
                    @deleted-custom-question="(question) => handleDeletedCustomQuestion(question)"
                />
            </div>

            <div v-if="step === 3">
                <div class="m-tb-40">
                    <div v-if="rating" class="fancy text-stone-500 pb-5">
                        {{ ratingSummary }} 
                    </div>

                    <img class="book-img" :src="book?.small_img_url || book.img_url" alt="">
                    <!-- Setting headlines -->
                    <CreatePostHeadline 
                        :headline-error="headlineError" 
                        :prop-headline="headline" 
                        :review-version="true"
                        @headline-changed="headlineHandler" 
                    />

                    <div class="divider m-tb-40"></div>

                    <YourReviewQuestions 
                        class="mt-0"
                        :is-viewing-review="true"
                        :is-comparison="false"
                        @question-form-completed="hasQuestionDataHandler()"
                        @go-to-edit-section="decrementStep"
                    />
                </div>

                <button 
                    type="button"
                    class="post-btn"
                    :disabled="step !== 3 || !isPostableData"
                    @click="emit('post-data')"
                >
                    {{ quickReview ? 'Move to shelf and post review' : 'Post' }}
                </button>
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
import ReviewRating from './ReviewRating.vue';
import { Bookshelves } from '../../../models/bookshelves';

const props = defineProps({
    headlineError: {
        type: String,
        required: false
        },
    book: {
        type: Object,
        required: false,
    },
    isPostableData: {
        type: Boolean,
        required: true,
    },
    /**
     * @description – param used to designate specific component instance where logic / functionality of createReviewPost may differ
     * @variant Bookshelves.currentlyReading.prefix this is for users that are moving books from currently reading into finished reading  
     */
    unique: {
        type: String,
        required: false,
    }
});

// get qs from data and add in entries.
const questionCats = Array.from(Object.keys(postData.posts.review))

// Refs
const book = ref(props.book ? props.book : null);
const { clone, debounce } = helpersCtrl;
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
const rating = ref(null);

// used to show certain question sets.
const questionMapping = reactive({
    'custom': customQuestions,
    'character': characterQuestions,
    'plot': plotQuestions,
    'tone': toneQuestions,
    // 'all': allQuestions,
});

const ratingMapping = {
    1: 'didn\'t love',
    2: 'liked',
    3: 'loved',
};

const ratingSummary = () => {
    return `You ${ratingMapping[rating.value]} ${ book.value.title || book.value.name }`;
};

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

function updateQuestionFromStore(){
    entries.value = store.arr
}

const throttledUpdateQuestionInEntries = debounce(updateQuestionFromStore, 200, false);

// emit handlers from child components.
const count = computed(() => {
    return store.arr.length
});

// 
function handleQuestionAdded(question) {
    entries.value.push(question)
}

function handleCustomQuestionAdded(question) {
    questionMapping.custom.push({
        "id": (question.id - 1),
        "q": '',
        "response": '',
        "is_spoiler": false,
        "placeholder": "Add your own response...",
        "isHiddenCustomQuestion": false
    });
}

function handleDeletedCustomQuestion(question) {
    // Dont remove first question from the UI ever.
    if(question.id === -1) {
        return
    }
    // console.log(questionMapping.custom.find((q) => q.id === question.id));
    // let questionToBeDelete = questionMapping.custom.find((q) => q.id === question.id);
    let indexOfQToBeDeleted = questionMapping.custom.indexOf((q) => q.id === question.id);
    questionMapping.custom.splice(indexOfQToBeDeleted, 1);
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

function setRatingAndIncrementStep(_rating) {
    rating.value = _rating;
    setTimeout(() => {
        incrementStep();
    }, 100);
}

// Add a watcher to emit up when something is added, doesn't seem to capture when entries
// loses entry with splice so we have duplicate above.
watch(entries, () => {
    let formattedData = helpersCtrl.formatReviewData(rating.value, entries.value, book.value, headline.value);
    emit('is-postable-data', formattedData)
});

watch(headline, () => {
    if(entries.value?.length) {
        emit('is-postable-data', helpersCtrl.formatReviewData(rating.value, entries.value, book.value, headline.value))
    }
})

watch(currentTopic, () => {
    characterQuestions = JSON.parse(JSON.stringify(postData.posts.review[currentTopic.value]));
});
// end of watchers

let quickReview = false;
// start of unique logic.
if (props.unique === Bookshelves.CURRENTLY_READING.prefix) {
    quickReview = true;
}
</script>

<style scoped>
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

.book-img {
    border-radius: var(--radius-md);
    margin-left: auto;
    margin-right: auto;
    height: 140px;
}
</style>