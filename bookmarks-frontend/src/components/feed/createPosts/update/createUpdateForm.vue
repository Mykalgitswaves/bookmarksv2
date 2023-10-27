<template>
    <div class="container grid">
        <CreatePostHeadline @headline-changed="headlineHandler" :review-type="'update'"/>
        
        <h3 class="text-2xl font-medium mb-2 mt-5 text-slate-600">Im on page <span class="italic text-indigo-600">{{ page }}</span></h3>
        
        <label class="input-number short" for="page-number">
            <input
                class="short rounded-md"
                id="page-number"
                type="number" 
                v-model="page"
            >
        </label>

        <h3 class="text-slate-600 font-medium text-2xl mb-2 mt-5">So far im thinking</h3>
        <label class="summary-update" for="summary-update">
            <textarea 
                class="rounded-md"
                name=""
                id="summary-update"
                cols="30"
                rows="10"
                v-model="update.response"
            />
        </label>

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
</template>
<script setup>
import { ref, watch, reactive } from 'vue';
import CreatePostHeadline from '../createPostHeadline.vue';
import { helpersCtrl } from '../../../../services/helpers';

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
    response: ''
})

function headlineHandler(e) {
    console.log(e, 'headline')
    update.headline = e;
}

watch(update, () => {
    return emit('update-complete', helpersCtrl.formatUpdateData(update));
});

</script>