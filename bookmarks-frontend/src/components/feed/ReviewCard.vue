<template>
    <div class="review-card-wrapper">
        <div class="review-card-top">
            <img :src="placeholderProfile" 
                alt="profile image"
                class="user-profile-img"
            />
            <p class="font-medium text-slate-600">{{ review.name }}</p>
        </div>
        <div>
            <p class="text-lg font-semibold text-slate-800 cursor-pointer"><RouterLink :to="workPage">Kitchen Confidential</RouterLink></p>
        </div>
        <div class="review-card-body">
            <p>{{ review.review_text }}</p>
        </div>
        <div class="review-card-bottom-toolbar">

        </div>    
    </div>
</template>

<script setup>
    import { defineProps, toRefs, computed } from 'vue';
    import { useRoute } from 'vue-router';
    import placeholderProfile from '@/assets/placeholder_user_1.jpg';

    const props = defineProps({
        review: {
            user_id: Number,
            name: String,
            review_text: String,
            
        }
    })
    const { review } = toRefs(props);

    // change this to be a value passed in as a prop later on. 
    const reviewID = 1;
    const route = useRoute();
    const workPage = computed(() => `/feed/${route.path.user}/works/${reviewID}`);
</script>

<style scoped>
    .review-card-wrapper {
        padding: 15px 20px;
        background-color: #F7FAFC;
        border-radius: .25rem;
    }
    .review-card-top {
        display: flex;
        align-items: center;
        justify-content: start;
    }
    .user-profile-img {
        height: 2.5rem;
        width: 2.5rem;
        aspect-ratio: 16 / 9;
        border-radius: 50%;
        margin-right: 1rem;
    }
    .review-card-body {

    }
    .review-card-bottom-toolbar {

    }

</style>