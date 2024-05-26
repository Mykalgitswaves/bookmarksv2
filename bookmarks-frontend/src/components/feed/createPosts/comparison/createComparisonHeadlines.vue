<template>
    <div> 
        <p class="text-slate-500 my-5 text-center">
            <span class="text-2xl text-stone-600 block fancy">Brevity is a luxury,</span>
            write two short headlines to summarize the commonalities shared by both books
        </p>
        
        <div class="comparator-headlines create">
            <label for="book1headline">
                <span class="mx-2 text-stone-600 text-sm underline text-center">{{ props.books[0]?.title }}</span>
                <input id="book1headline" type="text" v-model="models.comparator_a_headline">
            </label>

            <label for="book2headline">
                <span class="mx-2 text-stone-600 text-sm underline text-center">{{ props.books[1]?.title }}</span>
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
    },
    headlines: {
        type: Array,
        required: false,
    }
})

const models = reactive({
    comparator_a_headline: '',
    comparator_b_headline: ''
});

if (props.headlines) {
    models.comparator_a_headline = props.headlines[0];
    models.comparator_b_headline = props.headlines[1];
}

const emit = defineEmits(['headlines-changed']);

watchEffect(() => {
    emit('headlines-changed', models);
})
</script>