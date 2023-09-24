<template>
    <button
        v-if="!creating" 
        type="button"
        class="light-green-btn border-sm"
        @click="creating = true"    
    >
        <IconPlus/>
        <span class="ml-2">Add a question...</span>
    </button>

    <div v-if="creating">
        <label for="question" class="text-slate-600 italic">Question</label>
        <input
            id="question"
            type="text"
            class="text-start mb-5 text-lg question-border px-5 py-5 cursor-pointer box-btn active"
            v-model="q.q"
        >
        <label for="answer" class="text-slate-600 italic ">Answer</label>
        <textarea 
            class="border-2 block"
            id="answer"
            cols="" rows="7"
            v-model="q.response"
        ></textarea>
        
        <SpoilerRadioGroup :model-object="q" @is-spoiler-event="handleSpoilers"/>

        <button 
            type="button"
            class="py-3 rounded-md text-white bg-indigo-600 w-100 mt-5"
            @click="saveQuestionToSet(question=q.q, response=q.response, spoilers=q.is_spoiler)"
        >
            Add question
        </button>
    </div>
</template>
<script setup>
    import IconPlus from '../../svg/icon-plus.vue'
    import SpoilerRadioGroup from './spoilerRadioGroup.vue';
    import { ref, defineEmits } from 'vue'

    const emit = defineEmits();
    const creating = ref(false);
    const q = {}
    q.q = null;
    q.response = null;
    q.is_spoiler = null;

    function saveQuestionToSet(question, response, spoilers) {
        console.log(question, response, spoilers)
        console.log(q)
        creating.value = false;
        emit('custom-question', q)
    }

    function handleSpoilers(e) {
        q.is_spoiler = e.is_spoiler
    }
</script>
<style scoped>
    .light-green-btn {
        display: flex;
        background-color: #4f46e5;
        padding: .5rem;
        align-items: center;
        border-radius: .25rem;
        color: #fff;
        -webkit-transition: all .25s;
        -moz-transition: all .25s;
        transition: all .25s;
    }
    
    .light-green-btn:hover {
        transform: translate(1.05);
        -moz-transform: scale(1.05);
        -webkit-transform: scale(1.05);
    }

    input {
        width: 100%;
    }

    textarea { width: 100%; }

</style>