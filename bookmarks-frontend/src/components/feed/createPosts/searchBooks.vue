<template>
     <form class="grid grid-cols-1 gap-2" :class="{'w-100': props.centered}">
      <label v-if="props.labelAbove" for="search-book" class="text-gray-600 text-sm mb-2" :class="{'text-center': props.centered}">{{ props.labelAbove }}</label>
      
      <input
        id="search-book"
        class="py-2 px-4 rounded-md border-2 border-indigo-200 w-62 max-w-[600px]"
        :ref="(el) => (inputRef.push(el))"
        :class="{'mt-0': props.labelAbove, 
          'mt-5': !props.labelAbove,
          'w-100 mx-auto': props.centered
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

    <BookSearchResults 
      :style="maxHeight ? `max-height: ${maxHeight}; overflow-y: scroll;`: ''"
      :class="{'max-w-[600px]': !isMaxWidthUnset}"
      class="mx-auto" 
      :data="books" 
      :is-auth="true"
      :is-comparison="props.isComparison"
      @book-id="toParent"
    />
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
const isMaxWidthUnset = !!Object.keys(attrs).includes('max-width-unset')

async function searchBooks(e) {
  searchResultsArray.value = await db.get(urls.create.searchBook(e.target.value))
  console.log(searchResultsArray.value,'searchBookEndpoint')
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