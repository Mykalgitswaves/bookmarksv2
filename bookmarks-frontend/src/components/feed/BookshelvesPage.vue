<template>
    <BackBtn/>
    <section>
        <ul class="text-list">
            <li 
                v-for="(text, index) in textData"
                :key="index"
                class="text-list-item"    
            >
                {{ text }}
                <button 
                    type="button"
                    class="btn bg-indigo-500 text-white"
                    @click="removeDataFromWs(index)"    
                >
                    Remove
                </button>
            </li>
        </ul>

        <div>
            <input class="text-input mr-5 mb-10" type="text" v-model="modelData">
            <button 
            type="button"
            :disabled="posting"
            class="btn post-btn"
            @click="postToWS(modeldata)"
            >
                post
            </button>
        </div>

        <div class="flex justify-between w-50">

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
                @click="ws.unsubscribeFromSocketConnection()"    
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

const modelData = ref('');
const textData = ref([]);
const posting = ref(false);

async function postToWS() {
    posting.value = true;
    await db.post(urls.rtc.bookShelfTest(bookshelf),
        JSON.stringify(modelData.value), false
    ).then(() => {
        posting.value = false;
    });
}

async function removeDataFromWs(index){
    await db.put(urls.rtc.bookShelfTest(bookshelf),
        JSON.stringify(index), false
    )
}

watchEffect(() =>  {
    if(ws.data?.value){
        textData.value = ws.data.value
    }
})
</script>

<style scoped>
.text-input {
    min-width: 280px;
    max-height: 32px;
    padding: var(--padding-sm);
    border: 1px var(--stone-200) solid;
    border-radius: var(--radius-sm);
}

.post-btn {
    background-color: var(--green-300);
    color: var(--green-800);
}


.text-list {
    margin-bottom: 40px;
    margin-top: 20px;
}
.text-list-item {
    display: flex;
    justify-content: space-between;
    width: 280px;
     
}
</style>