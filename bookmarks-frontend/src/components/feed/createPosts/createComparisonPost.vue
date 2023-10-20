<template>
    <CreateComparisonSelection 
        @books-selected="booksHandlerFn"
    />
    
    <div v-if="books.length === 2">
        <div class="grid grid-cols-2 gap-5 max-w-[600px] my-5">
            <button 
                class="comparison-btn " 
                :class="{'active': currentView === 'add'}" 
                type="button"
                @click="currentView = 'add'"
            >
            Add comparison
            </button>

            <button 
                class="comparison-btn " 
                :class="{'active': currentView === 'view'}" 
                type="button"
                @click="currentView = 'view'"
            >
                View comparisons
            </button>
        </div>

        <KeepAlive>
            <CreateComparisonQuestionsVue 
                v-show="currentView === 'add'"
                :books="books"
                @postable-store-data="comparisonHandlerFn"
            />
        </KeepAlive>
        <KeepAlive>
            <ViewComparisonQuestionsVue
                v-show="currentView === 'view'"
            />
        </KeepAlive>
    </div>

    <div class="mobile-menu-spacer"></div>
</template>
<script setup>
import CreateComparisonSelection from './comparison/createComparisonSelection.vue';
import CreateComparisonQuestionsVue from './comparison/createComparisonQuestions.vue';
import ViewComparisonQuestionsVue from './comparison/viewComparisonQuestions.vue';
import { ref } from 'vue';

const books = ref([]);
const currentView = ref('add');

function booksHandlerFn(e) {
    console.log('working working working');
    books.value = e;
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
</style>