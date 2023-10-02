<template>
    <ul class="container questions">
        <li v-for="(question, i) in questions" :key="i">
            <div class="my-3 text-lg question-border px-5 py-5 cursor-pointer w-100 box-btn justify-between">
                <button type="button"
                    class="text-start"
                    @click="createPostResponseFormArr[i] = !createPostResponseFormArr[i]"
                    :ref="(el) => createPostResponseFormArr.push(el)"
                >
                        <span class="block">{{ question.q }}?</span>
                        <span class="block text-slate-400" :key="question.response">
                            {{ question.response }}
                        </span>
                </button>

                
            </div>
            <CreatePostResponseForm :q="question" v-if="!createPostResponseFormArr[i]"/>
        </li>
    </ul>
    
    
</template>
<script setup>
import { ref, computed } from 'vue';
import { createQuestionStore } from '../../../stores/createPostStore';
import CreatePostResponseForm from './createPostResponseForm.vue';
import IconRemove from '../../svg/icon-remove.vue';

const props = defineProps({
    isViewingReview: {
        type: Boolean,
        required: true,
    }
})

const store = createQuestionStore();
const questions = computed(() => store.arr ? store.arr : []);
const createPostResponseFormArr = ref([])

</script>

<style scoped>
.justify-between {
    display: flex;
    justify-content: space-between;
    padding-top: .5rem;
    padding-bottom: .5rem;
}


.box-btn-remove {
    color: #e11d48;
    width: 24px;
    height: 24px;
}

</style>