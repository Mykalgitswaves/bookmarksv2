<template>
    <section v-if="books.length === 2" class="mt-10">
        <CreateComparisonHeadlines class="mb-10" :books="books" @headlines-changed="$emit('headlines-changed', $data)"/>

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
            @question-added="$emit('question-added', $data)"
            @postable-store-data="$emit('postable-store-data', $data)"
        />

        <ViewComparisonQuestionsVue
            v-show="currentView === 'view'"
        />
    </section>
</template>
<script setup>
import { onUnmounted } from 'vue';
import CreateComparisonQuestionsVue from './comparison/createComparisonQuestions.vue';
import ViewComparisonQuestionsVue from './comparison/viewComparisonQuestions.vue';
import CreateComparisonHeadlines from './comparison/createComparisonHeadlines.vue';
import { createQuestionStore } from '../../../stores/createPostStore';

defineProps({
    currentView: {
        type: String,
        required: true,
        default: 'add',
    },
    books: {
        type: Array,
        required: true,
    },
    headlines: {
        type: Array,
        required: false,
    },
    questionCount: {
        type: Number,
        required: true,
    }
});
const store = createQuestionStore();

onUnmounted(() => {
    // Destroy old questions in store once you leave the page. This could pisss people off a bit idk.
    store.clearQuestions();
})

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