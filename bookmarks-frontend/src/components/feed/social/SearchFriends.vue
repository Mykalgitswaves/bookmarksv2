<template>
    <form class="grid grid-cols-1 gap-2">
      <label v-if="props.labelAbove" for="search-book" class="text-gray-600 text-sm">{{ props.labelAbove }}</label>
      
      <input
        id="search-user"
        class="py-2 px-4 rounded-md border-2 border-indigo-200 w-62 max-w-[600px]"
        :class="props.labelAbove ? 'mt-0' : 'mt-5'"
        v-model="searchData"
        @keyup="debouncedSearchRequest($event)"
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
const searchData = ref('')
const user = ref(null);

async function searchRequest(){
    await db.get(urls.user.searchUsersFriends(searchData.value)).then((res) => {
        searchResultsArray.value = res.data;
        console.log(res)
    });
}

const debouncedSearchRequest = debounce(searchRequest, 500, false)

</script>
<style scoped>
.user-search-results {
    max-width: 600px;
    background-color: var(--stone-100);
}
</style>