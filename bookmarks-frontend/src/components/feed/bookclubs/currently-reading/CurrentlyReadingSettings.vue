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
                <div v-if="!!data.currentlyReadingBook">
                    <SelectedBook :book="data.currentlyReadingBook" :set-book="true"/>

                    <ReadersPace :pace="{}"/>
                </div>

                <div v-else class="mt-10">
                    <SetCurrentlyReadingForm
                        v-if="data.isShowingSetCurrentBookForm"
                        @updated-current-book="(book) => {
                            data.currentlyReadingBook = book;
                            data.isShowingSetCurrentBookForm = false;
                        }"
                    />
                </div>
            </div>

            <div v-else class="mt-10 gradient fancy text-center text-xl loading-box">
                Loading settings
            </div>
        </TransitionGroup>
    </section>

    <div class="mobile-menu-spacer sm:hidden"></div>
</template>
<script setup>
import { db } from '../../../../services/db';
import { urls, navRoutes } from '../../../../services/urls';
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import SetCurrentlyReadingForm from './SetCurrentlyReadingForm.vue';
import SelectedBook from './SelectedBook.vue';
import ReadersPace from './ReadersPace.vue';

const route = useRoute();
const loaded = ref(false);
const data = ref({
    currentlyReadingBook: null,
    isShowingSetCurrentBookForm: true,
});

function loadData(){
    const currentlyReadingPromise = db.get(urls.bookclubs.getCurrentlyReadingForClub(route.params.bookclub), 
        null, true, 
        (res) => {
            data.value.currentlyReadingBook = res.currently_reading_book;   
        }, 
        (err) => {
            console.log(err);
        }
    );
     
    // const pacePromise = db.get()
    Promise.all([currentlyReadingPromise]).then(() => {
        loaded.value = true;
    });
}

loadData();
</script>