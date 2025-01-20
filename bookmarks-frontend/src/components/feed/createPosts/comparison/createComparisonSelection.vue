<template>
    <p v-if="!isDoneReviewing" class="text-center text-2xl mb-5 mt-5 font-semibold">The content monster is hungry for your thoughts 🍪. <br/>
        <span class="text-indigo-500">Start by picking two books to compare </span>
    </p>

    <button
        v-if="currentStep > 0 && !isDoneReviewing"
        type="button"
        class="ml-auto mr-auto mb-5 flex items-center gap-2 text-indigo-500 italic underline"
        @click="clearFirstBook()"
    >
        {{ firstBook }}
        <IconEdit style="height: 20px;"/>
    </button>
        
    <component
        v-if="!isDoneReviewing"
        :is="currentComponent.component"
        v-bind="currentComponent.props"
        v-on="currentComponent.events"
    ></component>

    <div v-if="isDoneReviewing" class="mt-15 flex container gap-5 justify-center">
        <p class="text-center fancy text-2xl text-stone-600">Comparing <span class="text-indigo-500">{{ books[0].title }}</span><br/> 
            & <span class="text-indigo-500">{{ books[1].title }}</span>
        </p>
        <!-- <button
            type="button"
            class="cursor-pointer text-indigo-600"
            alt="edit selection"
            @click="clearSecondBook()"
        >
            <IconEdit />
            <span class="underline hidden">Edit selection</span>
        </button> -->
    </div>
</template>
<script setup>
import { ref, reactive, watch, computed, onMounted } from 'vue';
import SearchBooks from '../searchBooks.vue';
import IconEdit from '../../../svg/icon-edit.vue';
import { db } from '../../../../services/db';
import { urls } from '../../../../services/urls';

const emit = defineEmits();
const books = ref([]);
const currentStep = ref(0);
const isDoneReviewing = ref(false);
const props = defineProps({
    bookId: { 
        type: String, 
        default: null 
    }
});

function bookOneHandler(e) {
    books.value = [e];
    currentStep.value = 1;
}

function bookTwoHandler(e) {
    books.value.push(e)
    emit('books-selected', books.value);
    isDoneReviewing.value = true;
}

function getFirstBook(){
    console.log('called getFirstBook FN')
    return books.value[0];
}

window.addEventListener('reset-book-selection', () => {
    clearSecondBook()
});

// hopefully this is flexible and vue doesnt fuck up. We can run  with this for a bit.
const bookMapping = reactive({
    0: {
        component: SearchBooks,
        props: {
            'label-above': 'Selecting book 1',
            'is-comparison': 'true',
            'centered': 'true',
        },
        events: {
            'book-to-parent': bookOneHandler,
        }
    },
    1: {
        component: SearchBooks,
        props: {
            'label-above': 'Selecting book 2',
            'is-comparison': 'true',
            'centered': 'true',
            'selected-book': getFirstBook,
        },
        events: {
            'book-to-parent': bookTwoHandler,
        },
    },
});

function getWorkPage(book_id) {
    db.get(urls.books.getBookPage(book_id), null, true, 
        (res) => { 
            books.value.push(res.data);
       }, 
       (err) => console.log(err)  
    )
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

// default component state is 0
if (props.bookId) {
    currentStep.value = 1;
}

// make reactive object in case we ever want more than two books for a comparison
const currentComponent = reactive({
    component: SearchBooks,
    props: bookMapping[currentStep.value].props,
    events: bookMapping[currentStep.value].events
})

watch(currentStep, (newValue) => {
        currentComponent.props = bookMapping[newValue].props
        currentComponent.events = bookMapping[newValue].events
})

const firstBook = computed(() => books.value.length ? books.value[0].title : 'Select a work');
const secondBook = computed(() => books.value.length > 1 ? books.value[1].title : 'Select a second work');

function clearFirstBook() {
        books.value.splice(0,1)
        currentStep.value--
}

function clearSecondBook() {
    books.value.splice(1,2);
    isDoneReviewing.value = false;
}
</script>