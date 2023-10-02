<template>
    <div class="container">
        <input
            class="px-2 py-2 rounded-md border-indigo-100 border-2 border-solid w-100 my-2"
            type="text"
            :value="q.q"
        />

        <textarea
            class="border-2 w-100"
            :name="q.id + '-question-text-area'"
            :id="q.id"
            cols="" rows="7"
            v-model="q.response"
        />

        <div class="flex gap-5 space-between items-end">
            <div>
                <label :for="q.id" class="flex items-center">
                    <span class="mr-5">Spoilers</span>
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
                    type="button"
                    class=" btn max-h-50 add-btn "
                    :class="{
                        'added': q.response !== '',
                    }"
                    @click="store.addOrUpdateQuestion(q)"
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
    }
})

const q  = toRaw(props.q)
console.log(q)
const store = createQuestionStore();
const emit = defineEmits();
</script>