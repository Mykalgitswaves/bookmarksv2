<template>
    <CreateComparisonSelection 
        @books-selected="booksHandlerFn"
    />
    
    <CreateComparisonQuestionsVue 
        v-if="books.length === 2"
        :books="books"
    />
    
    <div class="mobile-menu-spacer"></div>
</template>
<script setup>
import CreateComparisonSelection from './comparison/createComparisonSelection.vue';
import CreateComparisonQuestionsVue from './comparison/createComparisonQuestions.vue';
import { ref } from 'vue';

const books = ref([]);

function booksHandlerFn(e) {
    console.log('working working working')
    books.value = e;
}

</script>

<style scoped>

.comparison-images {
    aspect-ratio: 3/4;
    height: 150px;
    margin: 2ch 0;
}
</style>