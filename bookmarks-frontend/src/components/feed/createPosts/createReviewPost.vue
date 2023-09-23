<template>
    <p class="text-2xl mt-5 font-semibold">Start by picking a book 
    </p>
    <SearchBooks/>
<div v-if="hasBookSelected">
    <p class="text-2xl my-5 font-semibold">The content monster is hungry for your thoughts 🍪. 
        <span class="text-indigo-500 font font-medium"><br>Pick a genre and answer some questions.
        </span>
    </p>

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
                v-for="q in characterQuestions"
                :key="q.index"
            >
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
                    <TransitionGroup name="list" tag="li">
                        <div v-if="questionDict[q.id]">
                            <textarea 
                                class="border-2"
                                :name="q.type"
                                :id="q.index"
                                cols="" rows="7"
                                v-model="q.response"
                            ></textarea>
                            <div class="flex gap-5">
                                <button 
                                    type="button"
                                    class="block btn-add "
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
                    </TransitionGroup>
            </li>
    </ul>
    <p class="text-2xl my-5 text-indigo-500 font-medium">Or make your own questions</p>
    <div class="mobile-menu-spacer sm:hidden"></div>
</div>
</template>
<script setup>
import { ref, computed, toRaw, watch } from 'vue'
import { postData } from '../../../../postsData.js';
import { stateCtrl } from '../../../stores/createPostStore';
import SearchBooks from './searchBooks.vue';
const questionCats = Array.from(Object.keys(postData.posts.review))
console.log(questionCats)

const hasBookSelected = ref(false);
// Defaults to character, this change will dictate the questions rendered. we can model it.
const currentTopic = ref('character');

let characterQuestions = JSON.parse(JSON.stringify(postData.posts.review[currentTopic.value]));
const store = stateCtrl;


function loadAndUpdateState() {
    store.state()
    entries.value = [...store.toArray()]
    console.log(entries.value, 'Re-Loaded store')
}


const questionDict = ref({});
const entries = ref([]);
// we need a way to clone only the questions users select and then add those to our set but we need to be able to model our data after that.

// Watch to see if value changed and if it does then recreate object.
watch(currentTopic, () => {
    characterQuestions = JSON.parse(JSON.stringify(postData.posts.review[currentTopic.value]));
})

watch(entries.value, (oldValue, newValue) => {
        console.log(newValue, 'something deep changed')
})

</script>

<style scoped>
.text-white { color: #fff; }
.question-border {
    border: dotted 2px rgb(229 231 235);
    transition-duration: 250ms;
}

.question-border:hover {
    transform: scale(1.02);
    transition-duration: 250ms;
    border-color: rgb(129 140 248);
}

.active {
    border-color: rgb(70, 84, 213);
}

.btn-add {
    color: #fff;
    border-radius: .25rem;
    background-color: rgb(129 140 248);
    padding: .75rem 2rem;
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
    min-height: 350px
}
.questions .box-btn {
    width: 100%;
}
</style>