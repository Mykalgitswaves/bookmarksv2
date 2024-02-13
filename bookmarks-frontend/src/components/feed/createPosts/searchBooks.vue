<template>
     <form class="grid grid-cols-1 gap-2">
      <label v-if="props.labelAbove" for="search-book" class="text-gray-600 text-sm mb-2">{{ props.labelAbove }}</label>
      
      <input
        id="search-book"
        class="py-2 px-4 rounded-md border-2 border-indigo-200 w-62 max-w-[600px]"
        :ref="(el) => (inputRef.push(el))"
        :class="props.labelAbove ? 'mt-0' : 'mt-5'"
        @keyup="debouncedSearchBooks($event)"
        placeholder="Search for books"
        name="searchForBooks"
        type="text"
      />

      <label class="text-gray-600 text-sm" for="searchForBooks" v-if="!props.labelAbove">
        Tap a book and review it to add it to your shelf
      </label>
    </form>

    <BookSearchResults 
      class="max-w-[600px]" 
      :data="books" 
      :is-auth="true"
      :is-comparison="props.isComparison"
      @book-id="toParent"
    />
</template>
<script setup>
import { ref, reactive, computed, watch } from 'vue';
import BookSearchResults from '../../create/booksearchresults.vue';
import { db } from '../../../services/db';
import { urls } from '../../../services/urls';
import { helpersCtrl } from '../../../services/helpers';

const props = defineProps({
  labelAbove: {
    type: String,
    required: false
  },
  isComparison: {
    type: Boolean,
    required: false,
    default: false,
  }
})

const emit = defineEmits(['book-to-parent'])
const { debounce } = helpersCtrl;
const searchResultsArray = ref(null);
const book = ref(null);
const inputRef = ref([]);

async function searchBooks(e) {
  searchResultsArray.value = await db.get(urls.create.searchBook(e.target.value))
  console.log(searchResultsArray.value,'searchBookEndpoint')
}

const debouncedSearchBooks = debounce(searchBooks, 500, false)

function toParent(e) {
  book.value = e
  emit('book-to-parent', book.value)
}

const books = computed(() => (searchResultsArray.value && searchResultsArray.value.data ? searchResultsArray.value.data : ''))

watch(book, () => {
  if(props.isComparison && book.value !== null) {
    searchResultsArray.value = [];
  }
})
</script>