<template>
    <div>
        <div class="flex gap-6 my-5 items-center">
            <img 
                :src="props.books[0].img_url" 
                :alt="props.books[0].title" 
                class="comparison-images"
            >

            <img 
                :src="props.books[1].img_url"
                :alt="props.books[1].title" 
                class="comparison-images"
            >
        </div>
        
        <div>
            <ul>
                <li  
                    v-for="(topic, index) in topics"
                    :key="index"
                >
                    <button
                        class="question-topic" 
                        type="button"
                        @click="topicQuestions[topic] = !topicQuestions[topic]"
                    >
                        {{ topic }}
                        <IconChevron/>
                    </button>

                    
                    <TransitionGroup 
                        v-if="topicQuestions[topic]" 
                        class="grid grid-cols-1 gap-3 ml-2" 
                        tag="ul"
                    >
                        <li 
                            v-for="(q, index) in questions[topic]"
                            :key="index"
                        >
                            <button
                                class="add-topic" 
                                type="button"
                                @click="emit()"
                            >
                                <IconPlus/> 
                                <span class="ml-2">{{ q.comparison === '' ? 'click to add your own comparison' : q.comparison }}...</span>
                            </button>
                        </li>
                    </TransitionGroup>
                </li>
            </ul>
        </div>
    </div>
</template>
<script setup>
import { reactive } from 'vue';
import IconChevron from '../../../svg/icon-chevron.vue'; 
import IconPlus from '../../../svg/icon-plus.vue';
import { questions, topics } from './comparison';
const props = defineProps({
    books: {
        type: Array,
        required: true
    }
})
let topicQuestions = reactive({});

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