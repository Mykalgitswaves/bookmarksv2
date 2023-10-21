<template>
    <div class="card">
        <div class="card-header">
            <p class="text-slate-600"><span class="text-indigo-600 underline italic cursor-pointer">@{{ props.username }}</span> made a comparison</p>
        </div>
        <div class="card-content-main">
            <h3><span class="book-title-span-wrap">{{ props.book_title[0] }}</span> and <span class="book-title-span-wrap">{{ props.book_title[1] }}</span></h3>

            <div class="comparison-images">
                <img class="comparison-image" :src="props.small_img_url[0]" alt="">

                <IconLinkArrow />
                
                <img class="comparison-image" :src="props.small_img_url[1]" alt="">
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
            <div v-if="showReview[props.id] === true" >
                <div
                    class="comparison-headline-wrapper"
                >
                        <p class="comparison-headline">{{ props.headlines[0][0] }}</p>
                        <p class="comparison-headline">{{ props.headlines[0][1] }}</p>
                </div>

                <div class="card-responses">
                    <h3 class="text-indigo-600 text-xl font-semibold mb-4">Commonalities</h3>
                    <ul class="card-commonalities">
                        <li v-for="(comp, index) in props.comparators" :key="index">
                            {{ comp[0] }}
                        </li>
                    </ul>
                    <ul class="my-5">
                        <li 
                            v-for="(c, index) in props.comparisons" 
                            :key="index"
                            class="tab-commonalities"
                        >
                            <button 
                                type="button" 
                                class="text-indigo-600 text-2xl "
                                @click="comparisons[index] = true"
                            >
                                {{ props.comparators[index][0] }}
                            </button>

                            <p>{{ c[0] }}</p>
                        </li>  
                    </ul>
                </div>
            </div>
        </Transition>

        <div class="card-footer">
            
        </div>
    </div>
</template>
<script setup>
import IconLinkArrow from '../../svg/icon-arrow-link.vue';
import { reactive, ref } from 'vue';

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
const comparisonRefs = ref([])
// :headlines="post.book_specific_headlines"
// :book_title="post.book_title"
// :comparisons="post.responses"
// :comparator_ids="post.comparators"
// :created_at="post.created_date"
// :id="post.id"
// :username="post.user_username"
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Pinyon+Script&family=Tangerine&family=Ubuntu:wght@300;500&display=swap');
.card {
    text-align: center;
    border: 1px solid #A0AEC0;
    border-radius: 5px;
    margin-top: 1rem;
    margin-bottom: 1rem;
    max-width: 800px;
}

.card-header {
    padding: 15px 20px;
    border-bottom: 1px solid #A0AEC0;
}

.card-content-main {
    padding: 15px 20px;
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
.comparison-images {
    display: flex;
    column-gap: 20px;
    align-items: center;
    justify-content: center;
    color: #4f46e5;
}

.comparison-image {
    object-fit: cover;
    height: 137px;
    width: 100px;
}

.comparison-headline-wrapper {
    display: grid;
    grid-template-columns: 170px 170px;
    justify-content: center;
}
.comparison-headline {
    font-size: 44px;
    font-family: 'Tangerine', cursive;
    color: #4f46e5;
}
.card-footer {
    padding: 15px 20px;
}

.card-commonalities {
    gap: 1ch;
    display: grid;
    grid-template-columns: auto-fit, minmax(12ch, 1fr);
    justify-content: center;
    align-items: center;
}

.card-commonalities li {
    line-height: 2ch;
    border: 2px solid #818cf8;
    padding: 8px;
    color: #818cf8;
    border-radius: 4px;
    font-size: 16px;
    align-self: center;
    max-width: 12ch;
}

.tab-commonalities {
    width: 90%;
    text-align: start;
    margin-left: 25px;
    margin-right: 25px;
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