<template>
    <div class="bookclub-header">
        <div>
            <h1 class="text-3xl fancy text-stone-700">
                Currently Reading
            </h1>
            
            <p class="text-stone-500 mt-5">
                Set what book you're members are currently reading
            </p>
        </div>
    </div>
    <section>
        <TransitionGroup name="content" tag="div">
            <div v-if=loaded>
                <div v-if="currentlyReading?.id">

                </div>

                <div v-else class="mt-10">
                    <SetCurrentlyReadingForm @updated-current-book="(value) => console.log(value)"/> 
                </div>
            </div>

            <div v-else>
                <div class="gradient"></div>
            </div>
        </TransitionGroup>
    </section>
</template>
<script setup>
import { db } from '../../../../services/db';
import { urls, navRoutes } from '../../../../services/urls';
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import SetCurrentlyReadingForm from './SetCurrentlyReadingForm.vue';

const loaded = ref(false);
let currentlyReading = null;
const route = useRoute();

function loadCurrentlyReading(){
    db.get(urls.bookclubs.getCurrentlyReadingForClub(route.params.bookclub), 
        null, true, 
        (res) => {
            currentlyReading = res.currently_reading_book;
            loaded.value = true
        }, 
        (err) => {
            console.log(err);
            loaded.value = true;
        }
    );
}

loadCurrentlyReading();
</script>