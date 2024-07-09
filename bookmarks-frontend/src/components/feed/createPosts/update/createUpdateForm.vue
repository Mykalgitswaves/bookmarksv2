<template>
    <h1 class="create-post-heading-text text-center">Creating an update for <span class="create-post-heading-book-title">
            {{ book?.title }}</span>
        </h1>
    <!-- Controls for navigating to diff steps. -->
    <div>
        <div class="toolbar">
            <button type="button"
                class="toolbar-btn"
                :disabled="step === 1"
                @click="step -= 1"
            >
                <span v-if="step < 3">Previous</span>

                <span v-else>Edit</span>
            </button>

            <button type="button"
                class="toolbar-btn"
                :disabled="step === 3"
                @click="step += 1"
            >
                <span v-if="step < 2">Next</span>

                <span v-else>Finalize</span>
            </button>
        </div>


        <p class="text-stone-600 mb-5 mt-2 text-center"><span class="text-indigo-500">{{ step }}</span> / 3</p>

        <div class="toolbar-progress">
            <div class="total" :style="{'width': progressTotal + '%'}"></div>
            <div class="remaining" :style="{'width': remainderTotal + '%'}"></div>

            <span class="stepper one" :class="{'active': step >= 1}"></span>
            <span class="stepper two" :class="{'active': step >= 2}"></span>
            <span class="stepper three" :class="{'active': step >= 3}"></span>
        </div>
    </div>

    <div class="spacing-wrap">
        <div class="container">
            <div class="mb-5 ml-auto mr-auto w-90" v-if="step === 1">
                <label class="input-number block mb-5 mt-10" for="page-number">
                    <p class="text-2xl mb-2 mt-5 text-stone-600 fancy">Im on page <span class="italic text-indigo-600">{{ page }}</span></p>
                    <input
                        class="rounded-md"
                        id="page-number"
                        type="number" 
                        v-model="page"
                    >
                </label>

                <label for="summary-update" class="text-stone-600 fancy text-2xl mb-2 mt-5">
                    A quote that stuck
                    <span class="label-note">Add a quote to base your update off of</span>
                </label>

                <div class="summary-update no-max">
                    <textarea
                        class="rounded-md quote-summary"
                        name=""
                        id="summary-update"
                        v-model="update.quote"
                    />
                </div>
            </div>


            <div class="mb-5 w-90 ml-auto mr-auto" v-if="step === 2">
                <label class="block text-stone-600 fancy text-2xl mb-2 mt-5 " for="summary-update">
                    So far im thinking
                </label>
                <div  class="summary-update no-max">
                    <textarea class="rounded-md"
                        id="summary-update"
                        cols="30"
                        rows="10"
                        v-model="update.response"
                    />
                </div>
            </div>
            

            


            <div v-if="step === 3" class="ml-auto mr-auto">
                <CreatePostHeadline 
                    v-if="update.response.length"
                    :review-type="'update'"
                    :text-centered="true"
                    @headline-changed="headlineHandler" 
                />

                <h3 v-if="update.page" class="text-center fancy text-2xl mt-5 text-indigo-500">Page {{ update.page }}</h3>

                <div class="mt-5 mb-5">
                    <CreateUpdateFormResponses :update="update" @go-to-edit-section="step = 2"/>
                </div>

                <div v-if="update.response.length" class="flex gap-5 space-between items-end my-5" >
                    <div>
                        <label :for="update.id" class="flex items-center">
                            <input :id="update.id" 
                                type="checkbox"
                                v-model="update.is_spoiler"
                                value="true"
                                @change="emit('is-spoiler-event', update)"
                            />
                            <span class="text-slate-600 ml-2">Does this update contain spoilers?</span>
                        </label>
                    </div>
                </div>

                <button 
                    v-if="isPostableUpdate"
                    class="btn btn-submit w-100"
                    @click="emit('post-update', helpersCtrl.formatUpdateData(update))"
                >
                    post update
                </button>
            </div>
        </div>    
    </div>
</template>
<script setup>
import { ref, watch, reactive, computed } from 'vue';
import CreatePostHeadline from '../createPostHeadline.vue';
import CreateUpdateFormResponses from './CreateUpdateFormResponses.vue';
import { helpersCtrl } from '../../../../services/helpers';

const props = defineProps({
    book: {
        type: Object,
        required: true,
    },
});

const emit = defineEmits();
const headline = ref('');
const page = ref(0);
const step = ref(1);
const progressTotal = computed(() => Math.floor((step.value * 100) / 3));
const remainderTotal = computed(() => 100 - progressTotal.value);


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

const isPostableUpdate = computed(() => (update.response.length || update.page));

</script>
<style scoped>
 .spacing-wrap {
        height: 50%;
        min-height: 40vh;
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
