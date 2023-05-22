<template>
<div class="bg-slate-50 rounded-md w-100 mx-12 my-3 px-3 py-3 border-solid border-2 border-indigo-100 relative max-w-[500px]">
    <div class="review"> 
        <img class="h-24 hover:h-20 duration-300" src="../../../assets/losingmymindreview.png" alt="">
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
    ><span>
        <p class="inline mx-4 text-gray-500
            cursor-pointer font-medium
        ">Like</p>

        <p class="inline mx-4 text-gray-500
            cursor-pointer font-medium
        ">comment</p>
    </span>
    <p class-="inline text-gray-500 font-medium">1:23 pm 07/03/2023</p>
    </div>
</div>    
</template>

<script>
    

    export default {
        components: {
            
        },
        data() {
            return {
                fullDescShown: false,

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
    ". b b"
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
}

</style>