<template>
    <div style="min-width: 70vw; max-width: 600px;">
        <Input
            type="text" 
            class="fancy" 
            placeholder="Search for friends" 
            @update:model-value="(event) => debouncedSearch(event)" 
        />
    </div>
</template>
<script setup>
import { ref } from 'vue';
import { db } from '../../../../../services/db';
import { urls } from '../../../../../services/urls';
import { helpersCtrl } from '@/services/helpers'
import { Input } from '@/lib/registry/default/ui/input';

const props = defineProps({
    bookClubId: {
        type: String,
        required: true,
    }
});

const emit = defineEmits(['model-value:updated'])
// const modelData = ref('');
const { debounce } = helpersCtrl;

function search(data){
    db.get(urls.bookclubs.searchUsersNotInClub(props.bookClubId, data), null, false, 
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