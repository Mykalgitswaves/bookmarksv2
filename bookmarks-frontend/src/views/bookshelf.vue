<template>
    <div class="grid 
        place-content-center relative"
    >    
        <div class="mt-10">
            <BookReviews :reviews="reviews"/>
            <RecommendedBooks :recommendations="recommendations" />
        </div>
    </div>
</template>

<script>
import MainNav from '../components/bookshelf__reader/navbar.vue' 
import RecommendedBooks from '../components/bookshelf__reader/RecommendedBooks.vue'
import BookReviews from '../components/bookshelf__reader/BookReviews.vue'

    export default {
        components: {
            MainNav,
            RecommendedBooks,
            BookReviews
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
                    },
                    {
                        stars: 4,
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

<style scoped>
    .main-dash {
        display: grid;
        grid-template-columns: 2;
    }
</style>