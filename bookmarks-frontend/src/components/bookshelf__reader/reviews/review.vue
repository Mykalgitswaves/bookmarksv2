<template>
    <div class="rounded-md w-100 mx-12 my-3 px-3 py-3 relative max-w-[500px]">
        <div class="review">
            <div 
                :class="'w-10 absolute top-2' + `left-[${index + 1}px]`" 
                v-for="(index) in review.stars" :key="index">
                
                <span :class="'icon-star'">{{ index }}</span>
            </div>

            <img 
                class="h-24 hover:h-20 duration-300" 
                src="../../../assets/losingmymindreview.png" 
                alt="image preview of book"
            >
            
            <div> 
                <p class="text-xl font-semibold text-gray-800">{{ review.title }}</p>
                <p class="text-gray-600 text-sm">{{ truncatedDescription }}
                    
                    <span 
                        v-if="!fullDescShown"
                        class="text-gray-900 underline
                        cursor-pointer" 
                        @click="showFullDescription"
                    ><br/>... read more</span>

                    <span v-if="fullDescShown">{{ restOfDescription }}</span>
                </p>
            </div>
        </div>

        <div class="review-controls border-t-[1.5px]
            border-solid border-indigo-100 pt-2"
        >
            <span>
                <p class="inline mx-4 text-gray-500
                    cursor-pointer font-medium
                ">Like</p>

                <p 
                    v-if="review.comments"
                    @click="showComment = !showComment"
                    class="inline mx-4 text-gray-500
                    cursor-pointer font-medium
                ">{{ review.comments.length }} comments</p>
            </span>
            
            <p class="inline text-gray-500 font-medium text-sm">1:23 pm 07/03/2023</p>
        </div>
        <Comments 
            v-if="showComment"
            :comments="review.comments"
        />
    </div>

</template>

<script>
    import Comments from './comments.vue'

    export default {
        components: {
            Comments
        },
        data() {
            return {
                fullDescShown: false,
                showComment: false
            }
        },
        props: {
            review: {
                title: {
                    type: String,
                    required: true,
                },
                description: {
                    type: String,
                }
            }
        },
        methods: {
            showFullDescription() {
                this.fullDescShown = true;
                
            }
        },
        computed: {
            truncatedDescription() {
                return this.review.description.slice(0,150);
            },
            restOfDescription() {
                return this.review.description.slice(150, this.review.description.length)
            }
        }
    }
</script>

<style scoped>
    .review {
        display: grid;
        grid-template-areas: 
        "d b b"
        "a b b";
        grid-gap: 2ch;
        justify-content: center;
        align-items: center;
        max-width: 500px;
    }

    .review-controls {
        display: flex;
        flex-direction: row;
        width: 100%;
        justify-content: space-between;
        align-items: center;
    }

</style>