<template>
    <CreateComparisonSelection 
        @books-selected="booksHandlerFn"
    />

    <div v-if="books.length === 2">
        Comparing <span class="text-indigo-500">{{ books[0].title }}</span> and <span class="text-indigo-500">{{ books[1].title }}</span>
        <div>
            
        </div>
    </div>
</template>
<script setup>
import CreateComparisonSelection from './comparison/createComparisonSelection.vue';
import {ref, reactive} from 'vue';

let books = ref([]);

function booksHandlerFn(e) {
    console.log('working working working')
    books.value = e;
}

</script>