<template>
    <BackBtn/>
    <section>
        {{ count }}

        <div class="flex justify-between w-50">
            <button 
                type="button"
                :disabled="posting"
                class="btn "
                @click="postToWS()"
            >
                increment
                <span class="block text-sm text-slate-500">click this to see data being passed from another client!</span>
            </button>

            <button 
                type="button"
                class="btn bg-green-400"    
                @click="ws.createNewSocketConnection()"
            >
                open connection and add listeners
                <span class="block text-sm text-slate-500">click this first!</span>
            </button>

            <button 
                type="button"
                class="btn bg-indigo-300"
                @click="ws.unsubscribeFromSocketConnection"    
            >
                Close connection
                <span class="block text-sm text-slate-500">click this to end the connection!</span>
            </button>
        </div>
    </section>
</template>
<script setup>
import BackBtn from './partials/back-btn.vue';
import {
    ws
} from './bookshelves/bookshelvesRtc';
import {watchEffect, ref} from 'vue';
import { useRoute } from 'vue-router';

import { db } from '../../services/db';
import { urls } from '../../services/urls';

const route = useRoute();
const { user } = route.params;
const { bookshelf } = route.params;

const count = ref(0);
const posting = ref(false);

async function postToWS() {
    posting.value = true;
    count.value++
    await db.post(urls.rtc.bookShelfTest(bookshelf),
        JSON.stringify(count.value), false
    ).then(() => {
        posting.value = false;
    });
}

watchEffect(() =>  {
    if(ws.data?.value){
        count.value = parseInt(ws.data.value)
    }
})
</script>