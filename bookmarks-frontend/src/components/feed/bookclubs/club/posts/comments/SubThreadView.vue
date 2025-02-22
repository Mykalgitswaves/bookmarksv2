<template>
    <BackBtn />

    <!-- Post -->
    <AsyncComponent :promises=[loadPostPromise]>
        <template #resolved>
            {{ console.log(postData, 'post Data') }}
            <ClubPost :post="postData"/>
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
import { Thread, PostResponse } from '@/components/feed/bookclubs/club/posts/comments/threads';
import { currentUser } from '@/stores/currentUser';
// Components
import BackBtn from '@/components/feed/partials/back-btn.vue';
import AsyncComponent from '@/components/feed/partials/AsyncComponent.vue';
import ClubPost from '../ClubPost.vue';

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

const loadPostPromise = db.get(
            urls.concatQueryParams(
                urls.bookclubs.getClubFeed(bookclub), 
                { 'post_id': postId }
            ), 
            null, 
            false, 
            (res: PostResponse) => {
                console.log(res, 'loading the post data bruh');
                postData.value = res.posts;
            }, 
            (err: Error) => {
                console.error(err);
            }
        );
// #TODO: Fill out this other case (non club) next. 
 

/** @endLoad */
</script>
<style scoped>

</style>