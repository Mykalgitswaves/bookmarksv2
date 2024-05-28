<template>
    <CreateComparisonSelection 
        @books-selected="booksHandlerFn"
    />

    <div v-if="books.length === 2">
        <!-- Step 1 is creating responses for both -->
        <div class="mt-10">
            <div class="toolbar">
                <button type="button"
                    class="toolbar-btn"
                >
                    <span v-if="step === 1" @click="resetBookSelection">Change selection</span>

                    <span v-else @click="decrementStep">Edit</span>
                </button>

                <button type="button"
                    class="toolbar-btn"
                    @click="incrementStep"
                >
                    Finalize
                </button>
            </div>


            <p class="text-stone-600 mb-5 mt-2"><span class="text-indigo-500">{{ step }}</span> / 2</p>

            <div class="toolbar-progress">
                <div class="total" :style="{'width': progressTotal + '%'}"></div>
                <div class="remaining" :style="{'width': remainderTotal + '%'}"></div>

                <span class="stepper one" :class="{'active': step >= 1}"></span>
                <span class="stepper two" :class="{'active': step >= 2}"></span>
            </div>
        </div>

        <!-- Step 2 is viewing your created -->
        <CreateComparisonContentSection 
            :books="books" 
            :headlines="headlines"
            :current-view="currentView"
            :question-count="questionCount"
            :step="step"
            @headlines-changed="headlineHandler"
            @question-added="questionAddedFn"
            @postable-store-data="comparisonHandlerFn"  
            @go-to-books-selection="books = []"
            @go-to-edit-section="decrementStep"
        />

        <button 
            v-if="step === 2"
            type="button"
            class="post-btn"
            :disabled="!isPostableData"
            @click="emit('post-data')"
        >
            Post
        </button>
    </div>
</template>
<script setup>
import { ref, computed } from 'vue';
import CreateComparisonSelection from './comparison/createComparisonSelection.vue';
import CreateComparisonContentSection from './createComparisonContentSection.vue';

defineProps({
    isPostableData: {
        type: Boolean,
        required: true,
    }
});

const books = ref([]);
const currentView = ref('add');
const questionCount = ref(0);
const headlines = ref([]);
const step = ref(1);
const emit = defineEmits(['is-postable-data', 'set-headlines', 'post-data']);

function headlineHandler(headlineObj) {
    headlines.value = Object.values(headlineObj);
    emit('set-headlines', headlines.value);
}

function booksHandlerFn(e) {
    console.log('working working working');
    books.value = e;
}

function questionAddedFn(){
    currentView.value = 'view'
    questionCount.value++;
}

function comparisonHandlerFn(e) {
    emit('is-postable-data', e);
}

// navigate on forms. 
function incrementStep() {
    if(step.value < 2) {
        step.value += 1;
    }
}

function decrementStep() {
    if(step.value > 1) {
        step.value -= 1;
    }
}

function resetBookSelection(){
    const event = new CustomEvent('reset-book-selection', {
        detail: true,
    });
    window.dispatchEvent(event);
}

// for progress bar, duh.
const progressTotal = computed(() => Math.floor((step.value * 100) / 2));
const remainderTotal = computed(() => 100 - progressTotal.value);

</script>