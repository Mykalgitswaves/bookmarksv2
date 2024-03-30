<template>
    <CreateComparisonSelection 
        @books-selected="booksHandlerFn"
    />

    <CreateComparisonContentSection 
        :books="books" 
        :headlines="headlines"
        :current-view="currentView"
        :question-count="questionCount"
        @headlines-changed="headlineHandler"
        @question-added="questionAddedFn"
        @postable-store-data="comparisonHandlerFn"  
    />
</template>
<script setup>
import { ref } from 'vue';
import CreateComparisonSelection from './comparison/createComparisonSelection.vue';
import CreateComparisonContentSection from './createComparisonContentSection.vue';

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