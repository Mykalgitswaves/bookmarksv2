<template>
    <div class="
            col-span-2 md:col-span-1 col-start-1 col-end-2
            mb-20 mx-10 md:mt-40"
        >
            <div v-if="!isBooksHidden">
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
    import Recommendation from './recommendation.vue';

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