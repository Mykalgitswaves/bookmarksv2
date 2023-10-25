<template>
    <div class="card">
        <div class="card-header">
            <p class="text-slate-600"><span class="text-indigo-600 underline italic cursor-pointer">@{{ props.username }}</span> made a comparison</p>
        </div>
        <div class="card-content-main">
            <div class="comparisons">
                <div class="comparison">
                    <img class="comparison-image" :src="props.small_img_url[0]" alt="">
                    <p class="text-xl font-semibold">{{ props.book_title[0] }}</p>
                    <p class="comparison-headline">{{ props.headlines[0][0] }}</p>
                </div>

                <IconLinkArrow />

                <div class="comparison">
                    <img class="comparison-image" :src="props.small_img_url[1]" alt="">
                    <p class="text-xl font-semibold">{{ props.book_title[1] }}</p>
                    <p class="comparison-headline">{{ props.headlines[0][1] }}</p>
                </div>
            </div>
        </div>

        <button 
            v-if="!showReview[props.id]"
            type="button" 
            class="my-5 w-90 bg-indigo-600 text-white py-4 text-xl rounded-md"
            @click="showReview[props.id] = true"
        >
            Show comparison
        </button>

        <Transition>
            <div v-if="showReview[props.id] === true">

                <div class="card-responses">
                    <div class="divider"></div>

                    <h3 class="text-slate-700 text-lg my-2">Commonalities:</h3>

                    <ul class="my-3 content-start">
                        <li 
                            v-for="(c, index) in props.comparisons" 
                            :key="index"
                            class="card-commonalities"
                        >
                        
                            <h3>{{ props.comparators[index][0] }}</h3>
                            
                            <p class="mt-2 ml-2 text-slate-500">{{ c[0] }}</p>
                        </li>  
                    </ul>
                </div>
                           
                <div class="card-footer">
                    <button
                        type="button"
                        class="text-slate-600 flex items-center"
                    >
                        <IconComment/>
                        <span class="ml-2">comments</span>
                    </button>
                
                    <button 
                        type="button" 
                        class="text-slate-600 flex items-center"
                        :class="{'is-liked': isLiked}"
                        @click="AddLikeOrUnlike(props.id)"
                    >
                        <IconLike/>
                        <span class="ml-2">Like</span>
                    </button>
                </div>
            </div>
        </Transition>
    </div>
</template>
<script setup>
import IconLinkArrow from '../../svg/icon-arrow-link.vue';
import IconLike from '../../svg/icon-like.vue';
import IconComment from '../../svg/icon-comment.vue';
import IconChevron from '../../svg/icon-chevron.vue';

import { reactive, ref, } from 'vue';
import { db } from '../../../services/db';
import { urls } from '../../../services/urls';
import { useRoute } from 'vue-router'
const props = defineProps({
    book: {
        type: Array,
        required: true
    },
    book_title: {
        type: Array,
        required: true,
    },
    small_img_url: {
        type: Array,
        required: true
    },
    headlines: {
        type: Array,
        required: false,
    },
    comparisons: {
        type: Array,
        required: true
    },
    comparators: {
        type: Array,
        required: true
    },
    comparator_ids: {
        type: Array,
        required: true
    },
    createdAt: {
        type: String,
        required: true,
    },
    username: {
        type: String,
        required: true,
    },
    id: {
        type: String,
        required: true,
    },
    isIronic: {
        type: Boolean,
        required: false,
        default: false,
    },
    isAiGeneratedHeadlines: {
        type: Boolean,
        required: false,
        default: false
    }
})

const showReview = reactive({});
showReview[props.id] = false;

const comparisons = reactive({})
const isLiked = ref(null);
const route = useRoute();

async function AddLikeOrUnlike(id){
    const user_id = route.params.user
    await db.post(
        urls.reviews.likeComparison(user_id, id), true
        )
        .then((res) => {
            console.log(res)
            isLiked.value = true;
        });
}

</script>

<style scoped>

.card {
    text-align: center;
    border: 1px solid #A0AEC0;
    border-radius: 5px;
    margin-top: 1rem;
    margin-bottom: 1rem;
    max-width: 880px;
}

.card-header {
    padding: 15px 20px;
    border-bottom: 1px solid #A0AEC0;
}

.card-content-main {
    padding: 30px 20px;
}

.card-content-main h3 {
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 2ch;
}

.book-title-span-wrap {
    display: inline-block;
    overflow-wrap: break-word;
    width: 176px;
    font-size: 18px;
    font-weight: 600;
    font-style: italic;
    color: #4f46e5;
}
.comparisons {
    --comparisons-grid-columns: fit-content auto fit-content;
    display: grid;
    grid-template-columns: var(--comparisons-grid-columns);
    column-gap: 20px;
    align-items: start;
    justify-content: space-around;
    color: #4f46e5;

    @media screen and (min-width: 550px) {
        --comparisons-grid-columns: 1fr 20px 1fr;
    }
}

.comparisons > :nth-child(2) {
    --arrow-rotation: rotate(90deg);

    align-self: center;
    justify-self: center;
    transform: var(--arrow-rotation);
    margin: 20px;

    @media screen and (min-width: 550px) {
        --arrow-rotation: rotate(0deg);
    }
}

.comparison {
    display: grid;
    row-gap: 12px;
}

.comparison-image {
    object-fit: cover;
    height: 137px;
    width: 100px;
    justify-self: center;
}

.comparison-headline-wrapper {
    --headline-grid-column: 1fr 1fr;
    text-align: left;
    padding-left: 16px;
    padding-right: 16px;
    display: grid;
    grid-template-columns: var(--headline-grid-column);
}
.comparison-headline {
    font-size: 16px;
    font-weight: 500;
    text-align: center;
    color: #334155;
}

.card-footer {
    padding: 15px 20px;
    display: flex;
    justify-content: space-between;
}

.card-commonalities {
    justify-content: center;
    align-items: center;
    text-align: start;
    padding: 0 16px;
}

.card-commonalities h3 {
    font-size: 26px;
    line-height: 2ch;
    padding: 0 8px;
    color: #818cf8;
    text-align: start;
    font-style: italic;
}

.tab-commonalities {
    width: 90%;
    text-align: start;
    margin-left: 25px;
    margin-right: 25px;
}

.divider {
    border-bottom: 1px solid #e7e7e7;
    margin: 12px 25%;
}

.is-liked {
    color: #4f46e5;
}

.v-enter-active,
.v-leave-active {
  transition: opacity 0.5s ease;
}

.v-enter-from,
.v-leave-to {
  opacity: 0;
}
</style>