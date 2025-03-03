<template>
    <div v-if="!book">
        <p class="text-2xl mb-2 mt-5 font-semibold text-center">The content monster is hungry for your thoughts 🍪. <br/>
            <span class="text-indigo-500">Start by picking a book </span>
        </p>

        <SearchBooks @book-to-parent="bookHandler" :centered="true"/>
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
import { ref, toRaw, watch, onMounted } from 'vue';
import SearchBooks from './searchBooks.vue';
import CreateUpdateFormVue from './update/createUpdateForm.vue';
import { db } from '../../../services/db';
import { urls } from '../../../services/urls';

const props = defineProps({
    isPostableData: {
        type: Boolean,
        required: true,
    },
    bookId: {
        type: String,
        default: null,
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

function getWorkPage(book_id) {
    db.get(urls.books.getBookPage(book_id), null, true, 
      (res) => { 
          book.value = res.data 
       }, 
       (err) => console.log(err)  
  ); 
}

watch(
    () => props.bookId,
    (newBookId) => {
        if (newBookId) {
            getWorkPage(newBookId);
        }
    },
    { immediate: true } // Trigger immediately if book_id is provided at mount
);
</script>