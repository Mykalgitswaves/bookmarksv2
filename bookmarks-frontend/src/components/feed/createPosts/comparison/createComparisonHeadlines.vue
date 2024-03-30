<template>
    <div> 
        <p class="text-gray-600 my-5">
            <span class="text-2xl text-indigo-600 font-medium block">Brevity is a luxury,</span>
            write two short headlines to summarize the commonality shared by both books
        </p>
        
        <div class="comparator-headlines create">
            <label for="book1headline">
                <span class="mx-2 text-gray-700 text-lg underline">{{ props.books[0]?.title }}</span>
                <input id="book1headline" type="text" v-model="models.comparator_a_headline">
            </label>

            <label for="book2headline">
                <span class="mx-2 text-gray-700 text-lg underline">{{ props.books[1]?.title }}</span>
                <input id="book2headline" type="text" v-model="models.comparator_b_headline">
            </label>
        </div>
    </div>
</template>

<script setup>
import {reactive, watchEffect} from 'vue';

const props = defineProps({
    books: {
        type: Array,
        required: true,
    }
})
const models = reactive({
    comparator_a_headline: '',
    comparator_b_headline: ''
})

const emit = defineEmits(['headlines-changed']);

watchEffect(() => {
    emit('headlines-changed', models);
})
</script>