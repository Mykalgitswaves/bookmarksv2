<template>
    <div class="grid place-content-center relative">    
        <component :is="homeComponentMap" />
        
        <div class="mt-10 md:mt-20">
            <div 
                class="flex overscroll-auto overflow-y-hidden"
                v-for="review in reviews" 
                :key="review"
            > 
                <Review :review="review"/>
            </div>
        </div>

        <MainNav />
    </div>
    
</template>

<script>
import MainNav from '../components/bookshelf__reader/navbar.vue' 
import Review from '../components/bookshelf__reader/reviews/review.vue'
    export default {
        components: {
            MainNav,
            Review
        },
        data() {
            return {
                reviews: [
                    {
                        title: "Infinite bragging rights to liberal arts girlies",
                        description: "Read this one book, you probably dont even need to finish it. Just pop this baby down on a coffee table somewhere in plain view and watch how much undeserved attention you get from people that believe YOU actually had the discipline to read this bad boy"
                    },
                    {
                        title: "Infinite bragging rights to liberal arts girlies",
                        description: "Read this one book, you probably dont even need to finish it. Just pop this baby down on a coffee table somewhere in plain view and watch how much undeserved attention you get from people that believe YOU actually had the discipline to read this bad boy"
                    },
                    {
                        title: "Infinite bragging rights to liberal arts girlies",
                        description: "Read this one book, you probably dont even need to finish it. Just pop this baby down on a coffee table somewhere in plain view and watch how much undeserved attention you get from people that believe YOU actually had the discipline to read this bad boy"
                    },
                    {
                        title: "Infinite bragging rights to liberal arts girlies",
                        description: "Read this one book, you probably dont even need to finish it. Just pop this baby down on a coffee table somewhere in plain view and watch how much undeserved attention you get from people that believe YOU actually had the discipline to read this bad boy"
                    }
                ]
            }
        }
    }
</script>