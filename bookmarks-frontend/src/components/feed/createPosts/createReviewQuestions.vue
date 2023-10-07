<template>
    <ul>
        <li 
            v-for="(questionType, index) in qset"
            :key="index"
            :ref="(el) => activeQuestionCat.push(el)"
        >
            <button 
                class="question-topic"
                type="button"
                @click="activeQuestionCat[index] = !activeQuestionCat[index]"
            >
                <span>{{ questionType[0] }}</span>
                <IconChevron :class="{'active': activeQuestionCat[index]}"/>
            </button>

                <ul class="container questions" v-if="!activeQuestionCat[index]">
                    <li v-for="(question, i) in questionType[1]" :key="i">
                        <div class="my-3 text-lg question-border px-5 py-5 cursor-pointer w-100 box-btn">
                            <button type="button"
                                class="text-start"
                                :class="{'w-70': props.isViewingReview}"
                                @click="store.addOrUpdateQuestion(question)"
                            >
                                    <span class="block">{{ question.q }}?</span>
                                    <span class="block text-slate-400 text-start" :key="question.response">
                                        {{ question.response }}
                                    </span>
                            </button>

                            <button
                                v-if="props.isViewingReview"
                                disabled=""
                                class="text-red-600 w-20 box-btn-remove"
                                
                            >
                                <IconRemove />
                            </button>
                            <button 
                                v-if="!props.isViewingReview"
                                class="add-question"
                                @click="store.addOrUpdateQuestion(question)"
                            >
                                <IconAddPostVue/>
                            </button>
                        </div>
                    </li>
                </ul>
            </li>
        </ul>
</template>
<script setup>
import { toRaw, ref, watch } from 'vue';
import { helpersCtrl } from '../../../services/helpers';
import { createQuestionStore } from '../../../stores/createPostStore';
import IconAddPostVue from '../../svg/icon-add-post.vue';
import IconChevron from '../../svg/icon-chevron.vue';

const props = defineProps({
    questionMap: {
        type: Object,
        required: true,
    },
    isViewingReview: {
        type: Boolean,
        required: false,
    }
})
const { clone } = helpersCtrl;
const questionMap = (toRaw(props.questionMap))
const store = createQuestionStore();
// const questionMapClone = clone(questionMap);
const qset = Array.from(Object.entries(questionMap))
const activeQuestionCat = ref([])

activeQuestionCat.value.forEach((boolean) => (boolean.value = false));
</script>

<style scoped>

.question-topic {
    font-size: 18px;
    font-weight: semibold;
    display: flex;
    justify-content: space-between;
    margin: 1rem 0;
    padding: .75rem 1rem;
    width: 100%;
    border: solid 2px #e2e8f0;
    color: #1e293b;
    background: #f8fafc;
    border-radius: 4px;
    transition: all 150ms ease-in-out;
}

.active {
    transform: rotate(180deg);
}

.questions .box-btn {
    width: 100%;
    padding: 1ch;
    line-height: 1.2;
    display: flex;
    justify-content: space-between;
    align-items: center;
}


.box-btn-remove {
    display: flex;
    justify-content: flex-end;
    color: #e2e8f0;
    transition-duration: 250ms;
    transition-timing-function: ease;
}

.add-question {
    color: #818cf8;
}
</style>