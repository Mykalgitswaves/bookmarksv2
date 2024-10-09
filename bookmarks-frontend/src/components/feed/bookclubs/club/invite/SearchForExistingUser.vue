<template>
      <input
        id="search-for-existing-user"
        class="py-2 px-5 rounded-md border-[1px] border-indigo-200 w-100 fancy"
        placeholder="Search for friends"
        type="text"
        v-model="modelData"
        @keyup="debouncedSearch($event)"
      />
</template>
<script setup>
import { ref } from 'vue';
import { db } from '../../../../../services/db';
import { urls } from '../../../../../services/urls';
import { helpersCtrl } from '@/services/helpers'

const props = defineProps({
    bookClubId: {
        type: String,
        required: true,
    }
});

const emit = defineEmits(['model-value:updated'])
const modelData = ref('');
const { debounce } = helpersCtrl;

function search(){
    db.get(urls.bookclubs.searchUsersNotInClub(props.bookClubId, modelData.value), null, false, 
        (res) => {
            emit('model-value-updated', res.users);
        },
        (err) => {
            console.log(err);
        }
    );
} 

const debouncedSearch = debounce(search, 500, false);
</script>
<style scoped>

</style>