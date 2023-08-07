<template>
    <div class="flex pt-4">
        <button class="text-indigo-600 underline pr-5" @click="navigateBack">back</button>
        <h2 class="text-2xl font-medium text-slate-600">Kitchen Confidential</h2>
    </div>

    <WorkCard 
        :placeholder="placeholder"
        :card="card"
        :user="user"
    />

    <h2 class="text-2xl font-medium text-slate-600">Reviews of this work</h2>

    <ReviewCard 
        v-for="(review, index) in reviews" 
        :key="index"
        :review="review"
    />

    <SearchResults @search-results="handleData" :data="data"/>
</template>

<script setup>
    import WorkCard from '@/components/feed/WorkCard.vue';
    import ReviewCard from '@/components/feed/ReviewCard.vue';
    import SearchResults from '@/components/feed/navigation/SearchResults.vue'
    import { useRouter } from 'vue-router';
    import { ref } from 'vue';

    const router = useRouter()
    function navigateBack() {
        return router.back()
    }

    const reviews = [
        {
            id: 4, user_id: 1, book_name: 'Kitchen Confidential', rating: 4, review_dislikes: 1, review_likes: 10, name: 'Pilau', review_text: 'This book was crazy, I really liked it alot.'
        },
        {
            id: 4, user_id: 1, book_name: 'Kitchen Confidential', rating: 4, review_dislikes: 1, review_likes: 10, name: 'CashMoneyReviewData', review_text: 'This book was crazy, I really liked it alot.'
        },
        {
            id: 2, user_id: 2, book_name: 'Kitchen Confidential', rating: 4, review_dislikes: 1, review_likes: 10, name: 'Ala Wai Spa Experience', review_text: 'This book was crazy, I really liked it alot.'
        }
    ]

    const data = ref([]);

    function handleData(event) {
        console.log(event, 'testing')
        data.value = event;
    }

</script>

<style scoped>


</style>