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
            <KeepAlive>
                <button 
                    type="button"
                    :class="entries.includes(q) ? 'active' : ''"
                    class="text-start my-3 text-lg question-border px-5 py-5 cursor-pointer w-100 box-btn"
                    @click="questionDict[q.id] = q"
                >
                    <span class="block">{{ q.q }}?</span>
                    <span class="block text-slate-400" :key="q.response">
                        {{ q.response }}
                    </span>
                </button>
            </KeepAlive>
                
            <TransitionGroup name="list" tag="li">
                    <div v-if="questionDict[q.id] && q.id !== -1">
                        <textarea 
                            :ref="(el) => isAddDisabled(el)"
                            class="border-2"
                            :name="q.type"
                            :id="q.index"
                            cols="" rows="7"
                            v-model="q.response"
                            @change="isAddDisabled(el)"
                        ></textarea>
                        <div class="flex gap-5 space-between">
                            <div>
                                <SpoilerRadioGroup :model-object="q" @is-spoiler-event="handleSpoilers"/>
                            </div>

                            <div class="flex gap-5 items-end">
                                <button 
                                    :disabled="canAdd === false"
                                    type="button"
                                    class="block btn-add max-h-50"
                                    :class="q.response !== '' ? 'added' : ''"
                                    @click="store.add(q) && loadAndUpdateState()"
                                >
                                    <span v-if="!store.has(q)">Add response</span>
                                    <span v-if="store.has(q)">Response added</span>
                                </button>

                                <button
                                    type="button"
                                    class="px-3 py-3 bg-red-500 text-white rounded-md max-h-50"
                                    @click="questionDict[q.id] = null">
                                Hide
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
import { ref, defineEmits, toRaw, watch } from 'vue'
import { postData } from '../../../../postsData.js';
import { stateCtrl } from '../../../stores/createPostStore';
import { helpersCtrl } from '../../../services/helpers';
import SearchBooks from './searchBooks.vue';
import CreateYourOwnQuestions from './createYourOwnQuestions.vue';
import SpoilerRadioGroup from './spoilerRadioGroup.vue';

// get qs from data and add in entries.
const questionCats = Array.from(Object.keys(postData.posts.review))

// Refs
const book = ref(null);
const canAdd = ref(false);

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
const headline = ref('')
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
    console.log(entries.value, 'Re-Loaded store')
}

function bookIdHandler(e) {
    book.value = e;
}
// emits from child components.
function handleCustomQuestionEmit(e) {
    entries.value.push(e)
    questionMapping['Your post'] = entries.value;
    console.log(entries.value)
}
// looks for index of question being emitted by parent component and replaces question with spoiler boolean.
function handleSpoilers(e){
    const index = questionMapping[currentTopic.value].indexOf(e)
    questionMapping[currentTopic.value].splice(index, index + 1, e)
    console.log(questionMapping[currentTopic.value]);
}
// THis doesnt work but we want to make a function that
// doesnt allow people to allow empty strings as question answer pairs to avoid empty reviews.
// Should also check on backend.
function isAddDisabled(el) {
    ref(el).value > 5 ? canAdd.value = true : canAdd.value = false;
}

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

.btn-add {
    color: #fff;
    border-radius: .25rem;
    background-color: rgb(129 140 248);
    padding: .75rem 2rem;
    max-height: 50px;
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
}

.max-h-50 {
    max-height: 50px;
}

.border-indigo-500 {
    border-color: rgb(99 102 241);
}
</style>