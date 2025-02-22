<template>
    <BackBtn />

    <!-- Post -->
    <AsyncComponent :promises=[loadPost]>
        <template #resolved>
            {{ console.log(postData, 'post Data') }}
        </template>
        <template #loading></template>
    </AsyncComponent>
    <!-- Sub Thread -->
    <AsyncComponent :promise-factory="getCommentsFactory" :subscription-key="GET_COMMENTS_KEY">
        <template #resolved>
            {{ console.log(commentData, 'comment data') }}
        </template>
        <template #loading>
            World
        </template>
    </AsyncComponent>
</template>
<script setup lang="ts">
// Vue
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
// Services
import { db } from '@/services/db';
import { urls } from '@/services/urls';
import { Thread } from '@/components/feed/bookclubs/club/posts/comments/threads';
import { currentUser } from '@/stores/currentUser';
// Components
import BackBtn from '@/components/feed/partials/back-btn.vue';
import AsyncComponent from '@/components/feed/partials/AsyncComponent.vue';

// Params
const route = useRoute();
const router = useRouter();
const { bookclub, postId, subThreadId } = route.params;

// Data refs
const commentData = ref<Array<Thread> | []>([]);
const postData = ref({});

/**
 * @load_comments 
 */

const GET_COMMENTS_KEY = 'sub-thread-get-comments';

async function getCommentsFactory() {
    return db.get(urls.reviews.getCommentForComments(postId, subThreadId), null, false, (res: any) => {
        commentData.value = res.data.comments;
    }, (err: any) => console.warn(err));
};

async function loadPost() {
    if (bookclub) {
        db.get(urls.reviews.getPost(postId), null, false, (res: any) => {
            postData.value = res.data.post;
        });
    }
    // #TODO: Fill out this other case (non club) next. 
}
 

/** @endLoad */
</script>
<style scoped>

</style>