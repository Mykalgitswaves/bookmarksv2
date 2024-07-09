<template>
    <div class="spacing-wrap">
        <h1 class="create-post-heading-text">Creating an update for <span class="create-post-heading-book-title">
            {{ book?.title }}</span>
        </h1>

        <div class="container grid">
            <CreatePostHeadline @headline-changed="headlineHandler" :review-type="'update'"/>
            
            <div class="mt-5 mb-5">
                <label class="input-number short" for="page-number">
                    <p class="text-2xl font-medium mb-2 mt-5 text-slate-600">Im on page <span class="italic text-indigo-600">{{ page }}</span></p>
                    <input
                        class="short rounded-md"
                        id="page-number"
                        type="number" 
                        v-model="page"
                    >
                </label>
            </div>
            
            <div class="mb-5">
                <label for="summary-update" class="text-slate-600 font-medium text-2xl mb-2 mt-5">
                    A quote that stuck
                    <span class="label-note">Add a quote to base your update off of</span>
                </label>

                <div class="summary-update">
                    <textarea
                        class="rounded-md quote-summary"
                        name=""
                        id="summary-update"
                        v-model="update.quote"
                        :maxlength="MEDIUM_TEXT_LENGTH"
                    />
                </div>
            </div>


            <div class="mb-5">
                <label class="text-slate-600 font-medium text-2xl mb-2 mt-5" for="summary-update">
                    So far im thinking
                </label>
                <div  class="summary-update">
                    <textarea class="rounded-md"
                        id="summary-update"
                        cols="30"
                        rows="10"
                        v-model="update.response"
                        :maxlength="LARGE_TEXT_LENGTH"
                    />
                </div>
            </div>
            

            <div class="flex gap-5 space-between items-end">
                <div class="self-start">
                    <label :for="update.id" class="flex items-center">
                        <span class="text-slate-600 mr-2">Spoilers</span>
                        <input :id="update.id" 
                            type="checkbox"
                            v-model="update.is_spoiler"
                            value="true"
                            @change="emit('is-spoiler-event', update)"
                        >
                    </label>
                </div>
            </div>
        </div>    
    </div>
</template>
<script setup>
import { ref, watch, reactive } from 'vue';
import CreatePostHeadline from '../createPostHeadline.vue';
import { helpersCtrl } from '../../../../services/helpers';
import { MEDIUM_TEXT_LENGTH, LARGE_TEXT_LENGTH } from '../../../../services/forms'

const emit = defineEmits();
const headline = ref('');
const page = ref(0);
const props = defineProps({
    book: {
        required: true
    }

})

const update = reactive({
    headline: '',
    book_id: props.book.id,
    book_title: props.book.title,
    small_img_url: props.book.small_img_url,
    page: page.value,
    is_spoiler: false,
    response: '',
    quote: '',
})

function headlineHandler(e) {
    console.log(e, 'headline')
    update.headline = e;
}

watch(update, () => {
    return emit('update-complete', helpersCtrl.formatUpdateData(update));
});
</script>
<style scoped>
 .spacing-wrap {
        margin-top: var(--margin-md);
 }

.quote-summary {
    resize: none;
    height: 140px;
}

.label-note {
    display: block;
    font-size: var(--font-sm);
    color: var(--text-slate-600);
    font-weight: 300;
}
</style>
