<template>
    <div v-if="!book">
        <p class="text-2xl mb-2 mt-5 font-semibold">The content monster is hungry for your thoughts 🍪. <br/>
            <span class="text-indigo-500">Start by picking a book </span>
        </p>

        <SearchBooks @book-to-parent="bookHandler"/>
    </div>
    <CreateUpdateFormVue v-if="book" :book="book" @update-complete="updateEmitHandler"/>    
</template>

<script setup>
import { ref, toRaw } from 'vue';
import SearchBooks from './searchBooks.vue';
import CreateUpdateFormVue from './update/createUpdateForm.vue';

const emit = defineEmits();
const book = ref(null);
let update = null;

function bookHandler(e) {
    book.value = e;
}

function updateEmitHandler(e){
    update = toRaw(e);
    emit('is-postable-data', update);
}
</script>