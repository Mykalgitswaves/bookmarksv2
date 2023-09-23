<template>
    <div v-if="!book">
        <p class="text-2xl my-5 font-semibold">The content monster is hungry for your thoughts 🍪. <br/>
            <span class="text-indigo-500">Start by picking a book </span>
        </p>

        <SearchBooks @book-to-parent="bookIdHandler"/>
    </div>

    <div v-if="book" class="container">
        <div class="my-5">
            <p class="mb-2">You're reviewing <span class=" block italic text-indigo-500">{{ book.title }}</span></p>
            <p class="text-2xl font-medium">Pick a genre and answer some questions.</p>
        </div>

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
                    {{ q.q }}?
                    <span class="block text-slate-400" :key="q.response">
                        {{ q.response }}
                    </span>
                </button>
            </KeepAlive>
                
            <TransitionGroup name="list" tag="li">
                    <div v-if="questionDict[q.id]">
                        <textarea 
                            class="border-2"
                            :name="q.type"
                            :id="q.index"
                            cols="" rows="7"
                            v-model="q.response"
                        ></textarea>
                        <div class="flex gap-5 space-between">
                            <div>
                                <SpoilerRadioGroup :model-object="q" @is-spoiler-event="handleSpoilers"/>
                            </div>

                            <div class="grid grid-cols-2 gap-5">
                                <button 
                                    type="button"
                                    class="block btn-add"
                                    :class="q.response !== '' ? 'added' : ''"
                                    @click="store.add(q) && loadAndUpdateState()"
                                >
                                    <span v-if="!store.has(q)">Add response</span>
                                    <span v-if="store.has(q)">Response added</span>
                                </button>

                                <button
                                    type="button"
                                    class="px-3 py-2 bg-red-500 text-white rounded-md"
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


const questionCats = Array.from(Object.keys(postData.posts.review))

// Refs
const book = ref(null);
// Defaults to character, this change will dictate the questions rendered. we can model it.
const currentTopic = ref('character');
let characterQuestions = JSON.parse(JSON.stringify(postData.posts.review['character']));
let plotQuestions = JSON.parse(JSON.stringify(postData.posts.review['plot']));
let toneQuestions = JSON.parse(JSON.stringify(postData.posts.review['tone']));
let allQuestions = JSON.parse(JSON.stringify(postData.posts.review['all']));

const questionMapping = {
    'character': characterQuestions,
    'plot': plotQuestions,
    'tone': toneQuestions,
    'all': allQuestions
}

const store = stateCtrl;

const questionDict = ref({});
const entries = ref([]);
const spoilers = ref([])
// functions
const emit = defineEmits();

function loadAndUpdateState() {
    store.state()
    entries.value = [...store.toArray()]
    console.log(entries.value, 'Re-Loaded store')
}

function bookIdHandler(e) {
    book.value = e;
}

function handleCustomQuestionEmit(e) {
    entries.value.push(e)
    console.log(entries.value)
}

function handleSpoilers(e){
    const index = questionMapping[currentTopic.value].indexOf(e)
    questionMapping[currentTopic.value].splice(index, index + 1, e)
    console.log(questionMapping[currentTopic.value]);
}

watch(entries, () => {
    emit('is-postable-data', helpersCtrl.formatReviewData(entries.value, book.value.id, 'fix this at a later date'))
})

// Watch to see if value changed and if it does then recreate object.
watch(currentTopic, () => {
    characterQuestions = JSON.parse(JSON.stringify(postData.posts.review[currentTopic.value]));
})



</script>

<style scoped>
.text-white { color: #fff; }
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
    min-height: 250px
}
.questions .box-btn {
    width: 100%;
}


button {
    max-height: 50px;
}
</style>