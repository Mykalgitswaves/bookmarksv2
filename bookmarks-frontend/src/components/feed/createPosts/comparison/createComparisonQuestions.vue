<template>
    <div class="container mt-10">

        <p class="text-xl text-stone-700 font-medium mt-10">Add comparisons</p>

        <div class="select-1">
            <label for="comparison_dropdown">Pick a topic to create a comparison</label>
            <select 
                class="select-1"
                name="comparison dropdown"
                id="comparison_dropdown"
                v-model="topic"
                @change="(e) = (question.topic = e)"
            >
                <option 
                    v-for="(topic, index) in topics"
                    :key="index" 
                    :value="topic"
                >
                    {{ topic === 'custom' ? 'Custom' : `The ${topic} of both books...`  }}
                </option>
            </select>
        </div>
        <div class="summary-update comparison mt-5">
            <textarea name="" 
                id="" 
                cols="30" 
                rows="10"
                :placeholder="placeholder"
                v-model="question.comparison"
            />
        </div>

        <div class="flex space-between">
            <div>
                <div class="mt-5">
                    <label class="spoiler" for="comparisonSpoiler">
                        <input id="comparisonSpoiler" type="checkbox" value="true" v-model="question.is_spoiler">
                            <span class="mx-2 text-gray-600">Spoiler</span>
                    </label>
                </div>

                <div class="is_ai my-5">
                    <label for="add_irony">
                        <input type="checkbox" value="true" v-model="question.is_add_irony">
                            <IconIrony/>
                            <span class="text-gray-600">Add irony...</span>
                    </label>
                </div>
            </div>

            <button 
                class="add-comparison-btn"
                type="button"
                @click="addQuestionToStoreFn(question)"
            >
                Add
            </button>
        </div>
    </div>
</template>
<script setup>
import { ref, watch, toRaw } from 'vue';
import { questions, topics, Comparison, formatQuestionStoreForPost } from './comparison';
import { createQuestionStore } from '../../../../stores/createPostStore';
import IconIrony from '../../../svg/icon-irony.vue';

const props = defineProps({
    books: {
        type: Array,
        required: true
    },
    headlines: {
        type: Array,
        required: false,
    }
});

const store = createQuestionStore();
let question = new Comparison();
const topic = ref('')
const emit = defineEmits(['postable-store-data', 'question-added']);
const placeholder = ref('');

watch(topic, (newValue) => {
    placeholder.value = questions.find((q) => q.topic === newValue).q
})

async function addQuestionToStoreFn(question) {
    try { 
        question.topic = toRaw(topic.value);
        question.book_ids = [ props.books[0].id, props.books[1].id ];
        question.comparator_id = questions.find((q) => (topic.value === q.topic)).pk;
        question.small_img_url = [ props.books[0].small_img_url, props.books[1].small_img_url ]
        question.comparator_a_title = props.books[0].title;
        question.comparator_b_title = props.books[1].title;
        store.addOrUpdateQuestion(question);

        const postData = formatQuestionStoreForPost(store.arr, [props.headlines[0], props.headlines[1]]);

        emit('postable-store-data', postData)
        emit('question-added');

        resetQuestion()
    }
    catch(err) {
        console.error(err)
    }
};

function resetQuestion() {
    question = new Comparison();
    question.is_add_irony = false;
}

</script>

<style scoped>

.add-comparison-btn {
    padding: var(--padding-sm);
    background-color: var(--indigo-600);
    color: var(--surface-primary);
    align-self: center;
    border-radius: var(--radius-sm);
}

.add-topic {
    display: flex;
    align-items: center;
    color: #64748b;
    transition-duration: 150ms;
    text-align: left;
}

.add-topic:hover {
    color: #1e293b;
    transform: scale(1.05);
}

</style>