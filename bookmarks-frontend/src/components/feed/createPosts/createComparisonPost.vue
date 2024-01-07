<template>
    <CreateComparisonSelection 
        @books-selected="booksHandlerFn"
    />
    
    <section v-if="books.length === 2" class="mt-10">
        <CreateComparisonHeadlines class="mb-10" :books="books" @headlines-changed="headlineHandler"/>

        <div class="grid-two-btn-container">    
            <button
                type="button" 
                class="btn border-indigo-500 text-indigo-500 text-lg"
                @click="currentView = 'add'"
            >
                Add comparisons
            </button>

            <button 
                type="button"
                class="btn border-indigo-500 text-indigo-500 text-lg"
                @click="currentView = 'view'"
            >
                {{ questionCount }}
                comparisons
            </button>
        </div>

        <CreateComparisonQuestionsVue 
            v-show="currentView === 'add'"
            :books="books"
            :headlines="headlines"
            @question-added="questionAddedFn"
            @postable-store-data="comparisonHandlerFn"
        />

        <ViewComparisonQuestionsVue
            v-show="currentView === 'view'"
        />
    </section>
</template>
<script setup>
import CreateComparisonSelection from './comparison/createComparisonSelection.vue';
import CreateComparisonQuestionsVue from './comparison/createComparisonQuestions.vue';
import ViewComparisonQuestionsVue from './comparison/viewComparisonQuestions.vue';
import CreateComparisonHeadlines from './comparison/createComparisonHeadlines.vue';

import { ref } from 'vue';

const books = ref([]);
const currentView = ref('add');
const questionCount = ref(0);
const headlines = ref([]);

function headlineHandler(headlineObj){
    headlines.value = [
        headlineObj.comparator_a_headline,
        headlineObj.comparator_b_headline
    ]
}

function booksHandlerFn(e) {
    console.log('working working working');
    books.value = e;
}

function questionAddedFn(){
    currentView.value = 'view'
    questionCount.value++;
}

const emit = defineEmits(['is-postable-data']);

function comparisonHandlerFn(e) {
    emit('is-postable-data', e);
}

</script>

<style scoped>

.comparison-images {
    aspect-ratio: 3/4;
    object-fit: cover;
    height: 150px;
    margin: 2ch 0;
}

.comparison-btn {
    border: 2px solid #c7d2fe; 
    padding: 1rem 8px;
    font-size: 16px;
    color: #4f46e5;
    transition-duration: 200ms;
    transition-timing-function: ease-in-out;
    border-radius: 4px;
}

.active {
    background-color: #4f46e5;
    color: #fff;
    border-color: #4f46e5;
}

.border-indigo-500 {
    border: solid 2px var(--indigo-500);
}
</style>