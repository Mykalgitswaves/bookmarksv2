<template>
    <form class="set-current-book-form"
        @submit.prevent="setCurrentlyReadingBookForClub(formData)"
    >
        <div v-if="formData.formState === 1">
            <div>
                <h3 class="text-lg fancy text-stone-600">
                    Not currently reading anything
                </h3>
            
                <p class="text-sm text-stone-400">Use the form below to set your clubs currently reading book!</p>
            </div>
    
            <SearchBooks 
                unset-max-width
                :centered="true"
                :max-height="'50vw'" 
                @book-to-parent="(book) => {
                    formData.currentBook = book;
                    formData.formState += 1
                }"
            />
        </div>

        <div v-else-if="formData.formState === 2">
            <div>
                <button 
                    type="button"
                    class="underline text-stone-500 text-sm ml-auto" 
                    @click="() => {
                        formData.currentBook = null;
                        formData.formState -= 1;
                    }"
                >
                    select a different book
                </button>   

                <SelectedBook :book="formData.currentBook"/>

                <h3 class="mt-5 text-xl fancy text-stone-700 mb-5">
                  Set the pace for this book
                </h3>
            </div>

            <div class="pace-form px-4">
                <DatePicker @model-value-updated="(date) => {
                    formData.dateToFinish = date;
                }">
                    <template #helpText>
                        Pick a date you want to finish this book by
                    </template>
                </DatePicker>

                <div class="mt-5 grid-two-cols">
                    <div>
                        <p class="display-block text-sm text-stone-600">
                            How many chapters are in this book?
                        </p>
                        <input type="number" class="input-styles w-100" v-model="formData.chapters">
                    </div>

                    <div>
                        <p class="display-block text-sm text-stone-600">
                            How many pages are in this book?
                        </p>
                        <input type="number" class="input-styles w-100" v-model="formData.pages">
                    </div>
                </div>

                <div class="mt-5 pace-preview">
                    <h4>{{ pacePreview }}</h4>

                    <p class="mt-5 text-sm text-stone-500">
                        This estimation of pages per day may differ depending on the particular version of "{{ formData.currentBook?.title }}" your members have. 
                    </p>
                </div>

                <button 
                    class="mt-10 btn btn-wide btn-submit" 
                    type="submit" 
                    :disabled="!loaded"
                >
                    Set current book for club
                </button>
            </div>
        </div>
    </form>
</template>
<script setup>
import { db } from '../../../../services/db';
import { urls, navRoutes } from '../../../../services/urls';
import { ref, watchEffect, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import SearchBooks from '@/components/feed/createPosts/searchBooks.vue';
import SelectedBook from './SelectedBook.vue';
import DatePicker from '@/components/feed/partials/date-picker/DatePicker.vue';

const emit = defineEmits(['updated-current-book']);
const loaded = ref(true);
const formData = ref({
    currentBook: null,
    formState: 1, 
    dateToFinish: new Date(),
    chapters: null,
    pages: null,
});

const denominator = (1000 * 60 * 60 * 24);
const today = new Date();

const pacePreview = computed(() => {
    let form = formData.value;
    if (!form.pages || !form.dateToFinish) return 'Enter chapters and pages in order to see a page preview';
    let dayInTheFuture = new Date(form.dateToFinish);
    let diff = Math.abs(today - dayInTheFuture)
    let days = Math.ceil(diff / denominator);
    // Big number divided by the small number michael.
    let pagesPerDay = Math.ceil(form.pages / days);
    console.log(pagesPerDay, days, diff);
    console.assert(typeof pagesPerDay === 'number');
    return `Finishing this book by ${form.dateToFinish} will mean your readers will have to read ${pagesPerDay} pages per day`;
});

const route = useRoute();
const router = useRouter();

function setCurrentlyReadingBookForClub(formData) {
    loaded.value = false;
    let dateToFinish = formData.dateToFinish.toLocaleString();

    if (!formData.chapters || !formData.currentBook || !formData.pages) return null;
    
    const payload = { 
        expected_finish_date: dateToFinish,
        book: {
            id: formData.currentBook.id,
            chapters: formData.chapters,
        },
    };

    db.post(
        urls.bookclubs.setCurrentlyReadingBook(route.params.bookclub),
        payload,
        false,
        (res) => {
            emit('updated-current-book', formData.currentBook);
            loaded.value = true;
        }, 
        (err) => {
            console.log(err);
            loaded.value = true;
        }
    );
};
</script>
<style scoped>
.set-current-book-form {
    padding: 20px;
    background-color: var(--stone-50);
    border-radius: var(--radius-md);
}

.pace-preview {
    margin-left: auto;
    margin-right: auto;
    padding: 20px;
    border-radius: var(--radius-md);
    border: 1px solid var(--stone-600); 
    background-color: var(--stone-100);
}
</style>