<template>
    <div class="container max-w-[600px] mt-5">
            <p class="text-gray-600 my-5">
                <span class="text-2xl text-indigo-600 font-medium block">Brevity is a luxury,</span>
                write a short headline to summarize the commonality shared by both books
            </p>
            
            <div class="comparator-headlines">
                <label for="book1headline">
                    <span class="mx-2 text-gray-600">{{ props.books[0]?.title }}</span>
                    <input id="book1headline" type="text" v-model="comparator_a_headline">
                </label>

                <label for="book2headline">
                    <span class="mx-2 text-gray-600">{{ props.books[1]?.title }}</span>
                    <input id="book2headline" type="text" v-model="comparator_b_headline">
                </label>
            </div>

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
                        {{ topic === 'custom' ? 'Add your own' : `The ${topic} of both books...`  }}
                    </option>
                </select>
            </div>
            <div class="summary-update mt-5">
                <textarea name="" 
                    id="" 
                    cols="30" 
                    rows="10"
                    :placeholder="placeholder"
                    v-model="question.comparison"
                />
            </div>

            <div class="mt-5">
                <label class="spoiler" for="comparisonSpoiler">
                    <input id="comparisonSpoiler" type="checkbox" value="true" v-model="question.is_spoiler">
                        <span class="mx-2 text-gray-600">Spoiler</span>
                </label>
            </div>

            <div class="is_ai my-5">
                <label for="generate_ai">
                    <input id="generate_ai" type="checkbox" value="true" v-model="question.is_ai_generated">
                        <IconAi/>
                        <span class="text-gray-600">Generate headlines based of my content with LLM's</span>
                </label>
            </div>
            <div class="is_ai my-5">
                <label for="add_irony">
                    <input type="checkbox" value="true" v-model="question.is_add_irony">
                        <IconIrony/>
                        <span class="text-gray-600">Add irony...</span>
                </label>
            </div>

            <button 
                class="w-100 py-4 bg-indigo-500 rounded-sm text-white text-xl"
                type="button"
                @click="addQuestionToStoreFn(question)"
            >
                Add
            </button>
    </div>
</template>
<script setup>
import { ref, watch, toRaw } from 'vue';
import { questions, topics, Comparison, formatQuestionStoreForPost } from './comparison';
import { createQuestionStore } from '../../../../stores/createPostStore';
import IconAi from '../../../svg/icon-ai.vue';
import IconIrony from '../../../svg/icon-irony.vue';

const props = defineProps({
    books: {
        type: Array,
        required: true
    }
});
const store = createQuestionStore();
let question = new Comparison();
let comparator_a_headline;
let comparator_b_headline;
const topic = ref('')
const emit = defineEmits(['postable-store-data']);
const placeholder = ref('');

watch(topic, (newValue) => {
    placeholder.value = questions.find((q) => q.topic === newValue).q
})

function addQuestionToStoreFn(question) {
    question.topic = toRaw(topic.value);
    question.book_ids = [ props.books[0].id, props.books[1].id ];
    console.log(question.book_ids)
    question.comparator_id = questions.find((q) => (topic.value === q.topic)).pk;
    question.small_img_url = [ props.books[0].small_img_url, props.books[1].small_img_url ]
    question.comparator_a_title = props.books[0].title;
    question.comparator_b_title = props.books[1].title;
    store.addOrUpdateQuestion(question);
    question = new Comparison()
    const postData = formatQuestionStoreForPost(store.arr, [comparator_a_headline, comparator_b_headline]);
    emit('postable-store-data', postData)
}
</script>

<style scoped>

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