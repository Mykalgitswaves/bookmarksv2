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

        <div class="flex gap-5 space-between items-end mt-10">
            <div class="self-start">
                <label :for="q.id" class="flex items-center">
                    <input :id="q.id" 
                        type="checkbox"
                        v-model="q.is_spoiler"
                        value="true"
                        @change="emit('is-spoiler-event', q)"
                    >
                    <span class="ml-2">Spoilers</span>
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
    },
    indexOfQ: {
        type: Number,
    }
})

const q  = toRaw(props.q)

const store = createQuestionStore();
const emit = defineEmits(['store-changed']);

function alertQuestionWatch(question) {
    store.addOrUpdateQuestion(question)
    emit('store-changed', props.indexOfQ);
}
</script>