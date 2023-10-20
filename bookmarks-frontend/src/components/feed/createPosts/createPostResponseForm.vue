<template>
    <div class="container">
        <input
            v-if="!props.isComparison"
            class="px-2 py-2 rounded-md border-indigo-100 border-2 border-solid w-100 my-2"
            type="text"
            v-model="q.q"
            :placeholder="q.q"
        />

        <input 
            v-if="props.isComparison"
            class="px-2 py-2 rounded-md border-indigo-100 border-2 border-solid w-100 my-2"
            type="text"
            v-model="q.topic"
            :placeholder="q.topic"
        />

        <textarea
            v-if="!props.isComparison"
            class="border-2 w-100"
            :name="q.id + '-question-text-area'"
            :id="q.id"
            cols="" rows="7"
            v-model="q.response"
        />

        <textarea
            v-if="props.isComparison"
            class="border-2 w-100"
            :name="q.id + '-question-text-area'"
            :id="q.id"
            cols="" rows="7"
            v-model="q.comparison"
        />
        
        <div v-if="props.isComparison">
            <div class="comparator-headlines">
                <label for="book1headline">
                    <input id="book1headline" type="text" v-model="q.comparator_a_headline">
                </label>

                <label for="book2headline">
                    <input id="book2headline" type="text" v-model="q.comparator_b_headline">
                </label>
            </div>

            <div class="is_ai my-5">
                <label for="generate_ai">
                    <input id="generate_ai" type="checkbox" value="true" v-model="q.is_ai_generated">
                        <IconAi/>
                        <span class="text-gray-600">Generate headlines based of my content with LLM's</span>
                </label>
            </div>
        </div>

        <div class="flex gap-5 space-between items-end">
            <div class="self-start">
                <label :for="q.id" class="flex items-center">
                    <span class="mr-2">Spoilers</span>
                    <input :id="q.id" 
                        type="checkbox"
                        v-model="q.is_spoiler"
                        value="true"
                        @change="emit('is-spoiler-event', q)"
                    >
                </label>
            </div>

            <div>
                <button
                    v-if="!props.isComparison"
                    type="button"
                    class=" btn max-h-50 add-btn "
                    :class="{
                        'added': q.response !== '',
                    }"
                    @click="alertQuestionWatch(q)"
                >
                    Add response
                </button>

                <button
                    v-if="props.isComparison"
                    type="button"
                    class=" btn max-h-50 add-btn "
                    :class="{
                        'added': q.comparison !== '',
                    }"
                    @click="alertQuestionWatch(q)"
                >
                    Add response
                </button>

                <button
                    v-if="props.isViewingReview"
                    class="text-red-600 box-btn-remove "
                    @click="store.deleteQuestion(question)"
                    
                ><IconRemove /></button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { defineProps, toRaw } from 'vue'
import { createQuestionStore } from '../../../stores/createPostStore'
const props = defineProps({
    q: {
        type: Object,
        required: true,
    },
    isComparison: {
        type: Boolean,
        required: false,
    },
    isViewingReview: {
        type: Boolean,
        required: false,
        default: false,
    }
})

const q  = toRaw(props.q)

const store = createQuestionStore();
const emit = defineEmits();

function alertQuestionWatch(question) {
    store.addOrUpdateQuestion(question)
    emit('store-changed')
}
</script>