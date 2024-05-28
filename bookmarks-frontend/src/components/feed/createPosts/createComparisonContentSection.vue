<template>
    <section v-if="books.length === 2" class="mt-10">
        <div v-show="step === 1">
            <div class="mt-10 mb-10 text-center">
                <h4 class="heading">Click into a topic to add comparisons for your post.</h4>
                
                <p class="subheading">Pick from some pre-made prompts or add your own</p>
            </div>
            
            <CreateComparisonQuestionsVue 
                :books="books"
                :headlines="headlines"
                @question-added="$emit('question-added', $event)"
                @postable-store-data="$emit('postable-store-data', $event)"
            />
        </div>

        <div v-show="step === 2">
            <CreateComparisonHeadlines class="mb-10" :books="books" :headlines="headlines" @headlines-changed="$emit('headlines-changed', $event)"/>

            <div class="divider"></div>

            <ViewComparisonQuestionsVue @go-to-edit-section="emit('go-to-edit-section')"/>
            
            <div class="divider"></div>
        </div>
    </section>

    <div v-else>
        <h2 class="heading">Select two books to make a comparison</h2>
        
        <p class="subheading">Update your current selection 
            <button type="button"
                class="text-indigo-500 underline"
                @click="emit('go-to-books-selection')"
            >
                here
            </button>
        </p>
    </div>
</template>
<script setup>
import CreateComparisonQuestionsVue from './comparison/createComparisonQuestions.vue';
import CreateComparisonHeadlines from './comparison/createComparisonHeadlines.vue';
import ViewComparisonQuestionsVue from './comparison/viewComparisonQuestions.vue';
const emit = defineEmits(['go-to-books-selection', 'headlines-changed', 'go-to-edit-section']);

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
    },
    step: {
        type: Number,
        required: true,
    },
});

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