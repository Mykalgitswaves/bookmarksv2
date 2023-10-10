<template>
    <p v-if="!isDoneReviewing" class="text-2xl mb-5 mt-5 font-semibold">The content monster is hungry for your thoughts 🍪. <br/>
        <span class="text-indigo-500">Start by picking two books to compare </span>
    </p>

    <button
        v-if="currentStep > 0 && !isDoneReviewing"
        type="button"
        class="mb-5 flex items-center gap-2"
        @click="clearFirstBook()"
    >
        <IconEdit /><span class="text-indigo-500 italic">{{ firstBook }}</span>
    </button>

    <component
        v-if="!isDoneReviewing"
        :is="currentComponent.component"
        v-bind="currentComponent.props"
        v-on="currentComponent.events"
    ></component>

    <div v-if="isDoneReviewing" class="mt-15 flex space-between container gap-5">
        <p class="font-semibold text-left">Comparing <span class="text-indigo-500">{{ books[0].title }}</span> and <span class="text-indigo-500">{{ books[1].title }}</span></p>

        <button
            type="button"
            class="cursor-pointer text-indigo-600 px-2"
            alt="edit selection"
            @click="clearSecondBook()"
        >
            <IconEdit />
            <span class="underline hidden">Edit selection</span>
        </button>
    </div>
</template>
<script setup>

import { ref, reactive, watch, computed } from 'vue';
import SearchBooks from '../searchBooks.vue';
import IconEdit from '../../../svg/icon-edit.vue';

const emit = defineEmits();
const books = ref([]);
const currentStep = ref(0);
const isDoneReviewing = ref(false);

function bookOneHandler(e) {
    books.value = [e];
    currentStep.value = 1;
}


function bookTwoHandler(e) {
    books.value.push(e)
    emit('books-selected', books.value);
    isDoneReviewing.value = true;
}
// hopefully this is flexible and vue doesnt fuck up. We can run  with this for a bit.
const bookMapping = {
    0: {
        component: SearchBooks,
        props: {
            'label-above': 'Book 1',
            'is-comparison': 'true',
        },
        events: {
            'book-to-parent': bookOneHandler,
        }
    },
    1: {
        component: SearchBooks,
        props: {
            'label-above': 'Book 2',
            'is-comparison': 'true',
        },
        events: {
            'book-to-parent': bookTwoHandler,
        },
    },
};

// make reactive object in case we ever want more than two books for a comparison
const currentComponent = reactive({
    component: SearchBooks,
    props: bookMapping[currentStep.value].props,
    events: bookMapping[currentStep.value].events
})

// default component state is 0
currentComponent.value = bookMapping[0]

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