<template>
     <div class="bg-indigo-100 rounded-lg py-4 px-4 mx-auto">
        <textarea label="addpost" class="w-[100%]"></textarea>
        <div class="flex flex-row justify-end mt-2">
            <button class="bg-indigo-600 text-indigo-100 px-6 py-2 rounded-md">Add Review</button>
        </div>
     </div>
     <div class="mb-10 md:mt-20
            col-span-2 md:col-span-1 col-start-1 col-end-1
            border-solid border-b-2 border-indigo-100"
        >
            <h2 class="text-2xl my-5 text-slate-500 font-light">
                Reviews  
            </h2>
                <div 
                    class="flex justify-center md:justify-end"
                    v-for="review in pageItems" 
                    :key="review"
                > 
                    <Review :review="review"/>
                </div>
                <Pagination :pages="pages" @selected-page="handlePageSelection"/>
            </div>
</template>

<script>
import Review from './reviews/review.vue'
import Pagination from '../pagination.vue'

    export default {
        components: {
            Review,
            Pagination
        },
        props: {
            reviews: {
                type: Array,
                required: false
            }
        },
        data() {
            return {
                itemsPerPage: 3,
                pageItems: []
            }
        },
        methods: {
            handlePageSelection(page) {
               let startIndex = this.itemsPerPage * (page - 1)
               this.pageItems = this.reviews.slice(startIndex, startIndex + this.itemsPerPage)
            }
        },
        computed: {
            pages() {
                return Math.ceil(this.reviews.length / this.itemsPerPage)
            },
        },
        mounted() {
            this.handlePageSelection(1)
        }
    }
</script>