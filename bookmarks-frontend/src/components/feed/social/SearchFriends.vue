<template>
    <div class="search-user-form" role="form">
      <label v-if="props.labelAbove" for="search-book" class="text-gray-600 text-sm mb-2">{{ props.labelAbove }}</label>
      
      <input
        id="search-user"
        class="py-2 px-4 rounded-md border-2 border-indigo-200 w-62 max-w-[600px]"
        :class="props.labelAbove ? 'mt-0' : 'mt-5'"
        v-model="searchData"
        @keyup="debouncedSearchRequest($event)"
        placeholder="Search for friends"
        name="searchForUsers"
        type="text"
        :disabled="props.disabled"
      />

      <label class="text-gray-600 text-sm" for="searchForBooks" v-if="props.labelBelow">
        {{ props.labelBelow }}
      </label>
    </div>
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
    disabled: {
        type: Boolean,
        default: false,
    },
    bookshelfId: {
        type: String,
        required: true,
    },
});

const emit = defineEmits(['friends'])
const { debounce } = helpersCtrl;
const searchData = ref('');

async function searchRequest() {
    await db.get(urls.user.searchUsersFriends(searchData.value), { 'bookshelf_id': props.bookshelfId }).then((res) => {
        emit('search-friends-result', res);
    });
}

const debouncedSearchRequest = debounce(searchRequest, 500, false)

</script>
<style scoped lang="scss">
.user-search-results {
    max-width: 600px;
    background-color: var(--stone-100);
    margin-left: auto;
    margin-right: auto;
}

.search-user-form {
    margin-left: auto;
    margin-right: auto;
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: var(--margin-md);
    text-align: start;

    input {
        width: 100%;
    }
}
</style>