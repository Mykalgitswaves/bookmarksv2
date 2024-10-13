<template>
     <form class="grid grid-cols-1 gap-2" :class="{'w-100': props.centered}">
      <label v-if="props.labelAbove" for="search-book" class="text-gray-600 text-sm mb-2" :class="{'text-center': props.centered}">{{ props.labelAbove }}</label>
      
      <input
        id="search-book"
        class="py-2 px-4 rounded-md border-2 border-indigo-200 w-62"
        :ref="(el) => (inputRef.push(el))"
        :class="{'mt-0': props.labelAbove, 
          'mt-5': !props.labelAbove,
          'w-100 mx-auto': props.centered,
          'max-w-[600px]': !isUnsetMaxWidth
        }"
        placeholder="Search for books"
        name="searchForBooks"
        type="text"
        @keyup="debouncedSearchBooks($event)"
      />

      <label v-if="!props.labelAbove" 
        class="text-gray-600 text-sm" 
        :class="{ 'text-center': props.centered }"
        for="searchForBooks"
      >Tap a book to select it</label>
    </form>

    <TransitionGroup name="content">
      <div v-if="loading" class="mt-5 gradient fancy text-center text-xl loading-box">
        loading books
      </div>

      <BookSearchResults 
        v-if="!loading && books?.length"
        unset-max-width
        :style="maxHeight ? `max-height: ${maxHeight}; overflow-y: scroll;`: ''"
        class="mx-auto"
        :class="{'max-w-[600px]': !isUnsetMaxWidth}" 
        :data="books" 
        :is-auth="true"
        :is-comparison="props.isComparison"
        @book-id="toParent"
      />
    </TransitionGroup>
</template>
<script setup>
import { ref, computed, watch, useAttrs } from 'vue';
import BookSearchResults from '../../create/booksearchresults.vue';
import { db } from '../../../services/db';
import { urls } from '../../../services/urls';
import { helpersCtrl } from '../../../services/helpers';

const props = defineProps({
  labelAbove: {
    type: String,
  },
  isComparison: {
    type: Boolean,
    default: false,
  },
  centered: {
    type: Boolean,
    default: false,
  },
  selectedBook: {
    type: Function,
    default: () => '',
    required: false,
  },
  maxHeight: {
    type: String,
    required: false,
  }
});

const emit = defineEmits(['book-to-parent'])
const { debounce } = helpersCtrl;
const searchResultsArray = ref(null);
const book = ref(null);
const inputRef = ref([]);
const attrs = useAttrs();
const isUnsetMaxWidth = Object.keys(attrs).includes('unset-max-width');
const loading = ref(false);

async function searchBooks(e) {
  loading.value = true;
  searchResultsArray.value = await db.get(urls.create.searchBook(e.target.value), null, false, () => {
    loading.value = false;
  })
}

const debouncedSearchBooks = debounce(searchBooks, 500, false)

function toParent(e) {
  book.value = e
  emit('book-to-parent', book.value)
}

const books = computed(() => {
  if (searchResultsArray.value?.data) {
    searchResultsArray.value.data = searchResultsArray.value.data.filter((book) => book.id !== props.selectedBook()?.id)
    return searchResultsArray.value.data
  }
  return '';
})

watch(book, () => {
  if(props.isComparison && book.value !== null) {
    searchResultsArray.value = [];
  }
});
</script>