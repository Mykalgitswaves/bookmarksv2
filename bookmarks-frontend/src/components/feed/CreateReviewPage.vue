<template>
    <div class="relative">
        <BackBtn />
        <button
            v-if="postableData"
            type="button"
            class="bg-indigo-600 text-white post-btn"
            @click="postData(postableData)"
        >
            <IconAddPost/>
            post
        </button>

        <div class="ml-5">
            <component
                :is="mapping[reviewType]" 
                :key="postTypeMapping" 
                @is-postable-data="handlePost"
            />
        </div>
    </div>
    <div class="mobile-menu-spacer sm:hidden"></div>
</template>
<script setup>
    import { ref, defineAsyncComponent } from 'vue';
    
    import BackBtn from './partials/back-btn.vue';
    import IconAddPost from '../svg/icon-add-post.vue';
    
    import { useRoute } from 'vue-router';
    import { urls } from '../../services/urls';
    import { db } from '../../services/db';

    const createReviewPost = defineAsyncComponent(() => import('./createPosts/createReviewPost.vue'));
    const createUpdatePost = defineAsyncComponent(() => import('./createPosts/createUpdatePost.vue'));
    const createComparisonPost = defineAsyncComponent(() => import('./createPosts/createComparisonPost.vue'));

    const route = useRoute();
    const { work1, reviewType } = route.params;

    const mapping = {
        "review": createReviewPost,
        "update": createUpdatePost,
        "comparison": createComparisonPost,
    };

    const postableData = ref(null);

    function handlePost(data){
        postableData.value = data;
    }

    async function postData() {
        return await db.post(urls.reviews[reviewType], postableData, true);
    }
</script>
<style scoped>

.post-btn {
    position: absolute;
    top: 0;
    right: 0;
    display: flex;
    column-gap: 12px;
    border-radius: 4px;
    padding: 12px 16px;
}

</style>