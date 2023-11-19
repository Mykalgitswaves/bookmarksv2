<template>
    <BackBtn />
    <div class="ml-5">
        <component
            :is="mapping[reviewType]" 
            :key="postTypeMapping" 
            @is-postable-data="handlePost"
        />
        <button
            v-if="postableData"
            type="button"
            class="mt-5 bg-indigo-600 text-white post-btn"
        >
            post
        </button>
    </div>
</template>
<script setup>
    import BackBtn from './partials/back-btn.vue';
    import createReviewPost from './createPosts/createReviewPost.vue';
    import createUpdatePost from './createPosts/createUpdatePost.vue';
    import createComparisonPost from './createPosts/createComparisonPost.vue';
    import { ref } from 'vue';
    import { useRoute } from 'vue-router';

    const route = useRoute();
    const { work1, reviewType } = route.params;

    console.log(work1, reviewType, route.params);

    const mapping = {
        "review": createReviewPost,
        "update": createUpdatePost,
        "comparison": createComparisonPost,
    };

    const postableData = ref(null);
</script>
<style scoped>

.post-btn {
    padding: 12px 16px;
    border-radius: 4px;
    width: 400px;
}

</style>