<template>
    <div v-if="!book">
        <p class="text-2xl mb-2 mt-5 font-semibold">The content monster is hungry for your thoughts 🍪. <br/>
            <span class="text-indigo-500">Start by picking a book </span>
        </p>

        <SearchBooks @book-to-parent="bookHandler"/>
    </div>
    <div v-if="book">
        <CreateUpdateFormVue  :book="book" @update-complete="updateEmitHandler"/>

        <button 
            type="button"
            class="post-btn"
            :disabled="!isPostableData"
            @click="emit('post-data')"
        >
            Post
        </button>   
    </div>
</template>

<script setup>
import { ref, toRaw } from 'vue';
import SearchBooks from './searchBooks.vue';
import CreateUpdateFormVue from './update/createUpdateForm.vue';

defineProps({
    isPostableData: {
        type: Boolean,
        required: true,
    }
});

const emit = defineEmits(['post-data', 'is-postable-data']);
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