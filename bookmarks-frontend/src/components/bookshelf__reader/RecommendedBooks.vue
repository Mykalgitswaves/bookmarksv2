<template>
    <div class="
            col-span-2 md:col-span-1 col-start-1 col-end-2
            mb-20 mx-10 md:mt-40"
        >
            <h1 class="justify-start text-2xl 
                mb-2 text-slate-500 font-light"
            > Recommended books 
                <span 
                    class="ml-5 text-sm text-gray-800 cursor-pointer" 
                    @click="isBooksHidden = !isBooksHidden"
                >[hide]</span>
            </h1>
            <div v-if="!isBooksHidden">
            <label 
                class="hidden" 
                for="searchbooks"
            >
                Search by genre
            </label>

            <input 
                class="py-2 px-4 rounded-md my-1"
                type="text"
                name="searchbooks"
                placeholder="Search for a book"
            />
  
            <div 
                
                v-for="(recommendation, index) in recommendations" :key="index"
                class="grid grid-cols-1"
            >
                <Recommendation :recommendations="recommendations"/>
            </div>
            </div>
        </div>
</template>

<script>
    import Recommendation from './Recommendation.vue';

    export default {
        components: {
            Recommendation
        },
        props: {
            recommendations: {
                type: Array,
                required: false,
            }
        },
        data() {
            return {
                isBooksHidden: false,
            }
        }
    }
</script>