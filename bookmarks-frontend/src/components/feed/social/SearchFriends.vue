<template>
    <form class="grid grid-cols-1 gap-2">
      <label v-if="props.labelAbove" for="search-book" class="text-gray-600 text-sm">{{ props.labelAbove }}</label>
      
      <input
        id="search-book"
        class="py-2 px-4 rounded-md border-2 border-indigo-200 w-62 max-w-[600px]"
        :ref="(el) => (inputRef.push(el))"
        :class="props.labelAbove ? 'mt-0' : 'mt-5'"
        @keyup="debouncedSearchBooks($event)"
        placeholder="Search for friends"
        name="searchForUsers"
        type="text"
      />

      <label class="text-gray-600 text-sm" for="searchForBooks" v-if="props.labelBelow">
        {{ props.labelBelow }}
      </label>
    </form>

    <ul class="user-search-results">
        <li class="user">
            <div>
                <img class="h-10 w-10 rounded-full" />
            </div>
        </li>
    </ul>
</template>
<script setup>
import { ref } from 'vue'
import { db } from '../../../services/db';
import { urls } from '../../../services/urls';
import { helpersCtrl } from '@/services/helpers'

const props = defineProps({
    friendsOnly: {
        type: Boolean,
        default: false,
    },
    labelAbove: {
        type: String,
    },
    labelBelow: {
        type: String,
    },
});

const emit = defineEmits(['user-to-parent'])
const { debounce } = helpersCtrl;
const searchResultsArray = ref(null);
const user = ref(null);
const inputRef = ref([]);

</script>
<style scoped>
.user-search-results {
    max-width: 600px;
    background-color: var(--stone-100);
}
</style>