<template>
    <div> 
        <p class="text-slate-500 my-5 text-center">
            <span class="text-2xl text-stone-600 block fancy">Brevity's nice.</span>
            Write two short headlines to summarize the commonalities shared by both books
        </p>
        
        <div class="comparator-headlines create">
            <label for="book1headline">
                <img class="book-img" :src="books[0]?.small_img_url || book.img_url" alt="">

                <span class="mx-2 text-stone-600 text-sm underline text-center">{{ props.books[0]?.title }}</span>
                <input id="book1headline" type="text" v-model="models.comparator_a_headline" :maxlength="SMALL_TEXT_LENGTH">
            </label>

            <label for="book2headline">
                <img class="book-img" :src="books[1]?.small_img_url || book.img_url" alt="">

                <span class="mx-2 text-stone-600 text-sm underline text-center">{{ props.books[1]?.title }}</span>
                <input id="book2headline" type="text" v-model="models.comparator_b_headline" :maxlength="SMALL_TEXT_LENGTH">
            </label>
        </div>
    </div>
</template>

<script setup>
import {reactive, watchEffect} from 'vue';
import { SMALL_TEXT_LENGTH } from '../../../../services/forms';

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
    // Make sure when we set this that we are emitting upwards
    emit('headlines-changed', models);
}

const emit = defineEmits(['headlines-changed']);

watchEffect(() => {
    emit('headlines-changed', models);
})
</script>
<style scoped>
.book-img {
    border-radius: var(--radius-md);
    margin-left: auto;
    margin-right: auto;
    height: 140px;
}
</style>