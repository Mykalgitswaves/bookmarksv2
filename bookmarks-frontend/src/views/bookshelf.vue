<template>
    <div class="grid md_lg:grid-cols-5 sm:place-content-center
        relative mt-10">    
        <div class="mx-10 mb-20 md:mt-20 col-span-3">
            <h1 class="text-2xl mb-2 text-slate-500 font-light">
                Review Feed
            </h1>

            <div 
                class="flex overscroll-auto overflow-y-hidden"
                v-for="review in reviews" 
                :key="review"
            > 
                <Review :review="review"/>
            </div>
        </div>

        <div class="mb-20 mx-10 md:mt-40 col-span-2">
            <h1 class="text-2xl mb-2 text-slate-500 font-light">
                Recommended books
            </h1>

            <div 
                v-for="(recommendation, index) in recommendations" :key="index"
                class="grid grid-cols-1"
            >
                <Recommendations :recommendations="recommendations"/>
            </div>
        </div>

        <MainNav />
    </div>
    
</template>

<script>
import MainNav from '../components/bookshelf__reader/navbar.vue' 
import Review from '../components/bookshelf__reader/reviews/review.vue'
import Recommendations from '../components/bookshelf__reader/Recommendation.vue'
    export default {
        components: {
            MainNav,
            Review,
            Recommendations
        },
        data() {
            return {
                recommendations: [
                    {

                    },
                    {

                    },
                    {

                    },
                    {

                    }
                ],
                reviews: [
                    {
                        stars: 4,
                        title: "Infinite bragging rights",
                        description: "Read this one book, you probably dont even need to finish it. Just pop this baby down on a coffee table somewhere in plain view and watch how much undeserved attention you get from people that believe YOU actually had the discipline to read this bad boy",
                        comments: [
                            {
                                comment: "This thing was pretty meaty, i read like 20 pages before i updated my hinge to talk about a niche reference about Don Gately. So far it hasn't taken me anywhere",
                                stars: 4.2,
                                likes: 23,
                                replies: [
                                    {
                                    comment: "this is soooo dumb, like literally you are the problem here. This book was made to be read over a long period of time, not to",
                                    likes: 4,
                                    replies: []
                                    }
                                ]
                            }   
                        ]
                    },
                    {   
                        stars: 3,
                        title: "Infinite bragging rights",
                        description: "Read this one book, you probably dont even need to finish it. Just pop this baby down on a coffee table somewhere in plain view and watch how much undeserved attention you get from people that believe YOU actually had the discipline to read this bad boy",
                        comments: [

                        ]
                    },
                    {
                        stars: 2,
                        title: "Infinite bragging rights",
                        description: "Read this one book, you probably dont even need to finish it. Just pop this baby down on a coffee table somewhere in plain view and watch how much undeserved attention you get from people that believe YOU actually had the discipline to read this bad boy"
                    },
                    {
                        stars: 4,
                        title: "Infinite bragging rights",
                        description: "Read this one book, you probably dont even need to finish it. Just pop this baby down on a coffee table somewhere in plain view and watch how much undeserved attention you get from people that believe YOU actually had the discipline to read this bad boy"
                    }
                ]
            }
        }
    }
</script>