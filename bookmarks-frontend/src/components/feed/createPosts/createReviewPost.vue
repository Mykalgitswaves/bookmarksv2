<template>
    <div v-if="!book">
        <p class="text-2xl my-5 font-semibold">The content monster is hungry for your thoughts 🍪. <br/>
            <span class="text-indigo-500">Start by picking a book </span>
        </p>

        <SearchBooks @book-to-parent="bookIdHandler"/>
    </div>

    <div v-if="book" class="container">
        <div class="my-5">
            <p class="mb-2">You're reviewing <span class=" block italic text-indigo-500 font-semibold">{{ book.title }}</span></p>
        </div>

        <div class>
            <p class="text-2xl font-medium my-5 text-slate-600">Add a headline (TLDR) for your review.</p>
            
            <label 
                for="headline"
                class="block text-indigo-400 my-2"
            >This will appear front and center on your review</label>

            <input 
                id="headline" 
                type="text"
                placeholder="A masterpiece - someguy"
                class="border-indigo-500 border-solid border-2 rounded-md px-2 py-1 w-60"
                v-model="headline"
            >
        </div>

        <p class="text-2xl font-medium my-5 text-slate-600">Pick a topic to answer some questions.</p>

        <div class="radio-group">
            <label
                :for="cat"
                class="radio-select"
                v-for="(cat, index) in questionCats"
                :key="index"
            >
                <input :id="cat" type="radio" :value="cat" name="question-radios" v-model="currentTopic" @change="reloadQuestions">
                {{ cat }}
            </label>
        </div>

        <ul class="container questions" :key="characterQuestions">
            <li
                v-for="(q, index) in questionMapping[currentTopic]"
                :key="index"
            >
                <div class="my-3 text-lg question-border px-5 py-5 cursor-pointer w-100 box-btn">
                    <button type="button"
                        :class="entries.includes(q) ? 'active' : ''"
                        class="w-70 text-start"
                        @click="questionDict[q.id] = q.id"
                    >
                            <span class="block">{{ q.q }}?</span>
                            <span class="block text-slate-400" :key="q.response">
                                {{ q.response }}
                            </span>
                    </button>

                    <button 
                        :disabled="!entries.includes(q)"
                        class="text-red-600 w-20 box-btn-remove"
                        @click="removeQuestionFromEntries(q, index)"
                    >
                        <IconRemove />
                    </button>
                </div>
            
                
            <TransitionGroup name="list" tag="li">
                    <div v-if="questionDict[q.id] === q.id">
                        <textarea 
                            :ref="(el) => (elementRefs[index] = el)"
                            class="border-2"
                            :name="q.type"
                            :id="q.index"
                            cols="" rows="7"
                            v-model="q.response"
                        ></textarea>
                        <div class="flex gap-5 space-between items-end">
                            <div>
                                <SpoilerRadioGroup :model-object="q" @is-spoiler-event="handleSpoilers"/>
                            </div>
                            <div>
                                <button
                                    :ref="(el) => (buttonRefs[index] = el)"
                                    type="button"
                                    class=" btn max-h-50 add-btn "
                                    :class="{
                                        'added': q.response !== '',
                                    }"
                                    @click="addToState(q)"
                                >
                                    <span v-if="!store.has(q)">Add response</span>
                                    <span v-if="store.has(q)">Response added</span>
                                </button>
                                <button 
                                    type="button"
                                    class="ml-5 btn max-h-50 bg-amber-300"
                                    @click="questionDict[q.id] = null"
                                >Hide
                                </button>
                            </div>
                        </div>
                    </div>
                </TransitionGroup>
            </li>
        </ul>

        <div>
            <p class="text-2xl my-5 text-indigo-500 font-medium">Or make your own questions</p>
            <CreateYourOwnQuestions @custom-question="handleCustomQuestionEmit"/>
        </div>

        <div class="mobile-menu-spacer sm:hidden"></div>
    </div>
</template>
<script setup>
import { ref, defineEmits, toRaw, watch, watchEffect } from 'vue'
import { postData } from '../../../../postsData.js';
import { stateCtrl } from '../../../stores/createPostStore';
import { helpersCtrl } from '../../../services/helpers';
import SearchBooks from './searchBooks.vue';
import CreateYourOwnQuestions from './createYourOwnQuestions.vue';
import SpoilerRadioGroup from './spoilerRadioGroup.vue';
import IconRemove from '../../svg/icon-remove.vue';
// get qs from data and add in entries.
const questionCats = Array.from(Object.keys(postData.posts.review))

// Refs
const book = ref(null);

// Defaults to character, this change will dictate the questions rendered. we can model it.
const currentTopic = ref('Your post');
// clones of our fixture data.
let characterQuestions = JSON.parse(JSON.stringify(postData.posts.review['character']));
let plotQuestions = JSON.parse(JSON.stringify(postData.posts.review['plot']));
let toneQuestions = JSON.parse(JSON.stringify(postData.posts.review['tone']));
let allQuestions = JSON.parse(JSON.stringify(postData.posts.review['all']));
const viewEntriesDefault = JSON.parse(JSON.stringify(postData.posts.review['Your post']))
const store = stateCtrl;

const questionDict = ref({});
const entries = ref([]);
const headline = ref('');
const elementRefs = ref([]);
const buttonRefs = ref([]);
// used to show certain question sets.
const questionMapping = {
    'character': characterQuestions,
    'plot': plotQuestions,
    'tone': toneQuestions,
    'all': allQuestions,
    'Your post': entries.value.length > 0 ? entries.value : viewEntriesDefault,
}

// functions
const emit = defineEmits();

// updates state, duh.
function loadAndUpdateState() {
    store.state()
    entries.value = [...store.toArray()]
    questionMapping['Your post'] = entries.value;
}

function bookIdHandler(e) {
    book.value = e;
}

// emit handlers from child components.

function handleCustomQuestionEmit(e) {
    store.add(e)
    entries.value = [...store.toArray()]
    questionMapping['Your post'] = entries.value;
}

// looks for index of question being emitted by parent component and replaces question with spoiler boolean.
function handleSpoilers(e){
    const index = questionMapping[currentTopic.value].indexOf(e)
    questionMapping[currentTopic.value].splice(index, index + 1, e)
}

function removeQuestionFromEntries(q, index) {
    // delete is not working.
    // Remove from entries. then emit new object;
        store.delete(q)
        questionMapping[currentTopic.value][index].response = ''
        if(currentTopic.value === 'Your post') {
            questionMapping[currentTopic.value] = JSON.parse(JSON.stringify(postData.posts.review['Your post']));
        }
        emit('is-postable-data', entries.value)
}

function addToState(q) {
    store.add(q);
    loadAndUpdateState(); 
    // auto close toggles on this.
    questionDict[q.id] = false;
};
// Add a watcher to emit up when something is added, doesn't seem to capture when entries loses entry with splice so we have duplicate above.
watch(entries, () => {
    emit('is-postable-data', helpersCtrl.formatReviewData(entries.value, book.value.id, headline.value))
})

// Watch to see if value changed and if it does then recreate object.
watch(currentTopic, () => {
    characterQuestions = JSON.parse(JSON.stringify(postData.posts.review[currentTopic.value]));
})
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

.mobile-menu-spacer {
    height: 5rem;
    width: auto;
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

.questions {
    min-height: 250px;
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
    justify-content: flex-end;
    color: #e2e8f0;
    transition-duration: 250ms;
    transition-timing-function: ease;
}

.box-btn-remove:hover:not([disabled]) {
    color: rgb(220 38 38);
}

.max-h-50 {
    max-height: 50px;
}

.border-indigo-500 {
    border-color: rgb(99 102 241);
}

.bg-amber-300 {
    background-color: #fde68a;
}
</style>