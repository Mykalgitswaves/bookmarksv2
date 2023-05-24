<template>
     <div class="mb-10 md:mt-20
            col-span-2 md:col-span-1 col-start-1 col-end-1
            border-solid border-b-2 border-indigo-100"
        >
            <h1 class="text-2xl mb-10 text-slate-500 font-light ml-10">
                Review Feed  
                <span 
                    class="ml-5 text-sm text-gray-800 cursor-pointer" 
                    @click="isReviewsHidden = !isReviewsHidden"
                >[hide]</span>
            </h1>

            <div v-if="!isReviewsHidden">
                <div 
                    class="flex justify-center md:justify-end"
                    v-for="review in reviews.slice(0,3)" 
                    :key="review"
                > 
                    <Review :review="review"/>
                </div>

                <button 
                    class="ml-10 px-4 py-2 bg-indigo-600 
                    rounded-md text-gray-200 mb-10 
                    hover:bg-indigo-800 duration-200"
                    @click="showMoreReviews"
                >
                    more reviews
                </button>
            </div>
            <div v-if="isReviewsHidden" class="w-[50vw]"></div>
        </div>
</template>

<script>
import Review from './reviews/review.vue'
    export default {
        components: {
            Review
        },
        props: {
            reviews: {
                type: Array,
                required: false
            }
        },
        data() {
            return {
                isReviewsHidden: false,
            }
        }
    }
</script>