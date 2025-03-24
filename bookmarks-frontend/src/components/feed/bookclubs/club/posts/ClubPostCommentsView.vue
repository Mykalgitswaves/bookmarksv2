<template>
    <div class="border">
        <BackBtn :back-fn="() => $router.push(navRoutes.toBookClubFeed(user, bookclub))"/>
        <!-- Load the post first. -->
        <AsyncComponent :promises="[getPostPromise]">
            <template #resolved>
                <div class="post-wrap">
                    <ClubPost :post="data.post" :is-viewing-post="true"/>
                    
                    <ViewAwards/>
                </div>

                <ClubPostCommentBar :post-id="data.post.id" :comment="clubCommentSelectedForReply" @stop-commenting="clubCommentSelectedForReply = null"/>
            </template>
            <template #loading>
                <div class="fancy loading gradient radius-sm py-5 text-center mb-5">Loading post...</div>
            </template>
        </AsyncComponent>
        
        <!-- Then load the comments as separate components -->
        <AsyncComponent :promises="[getPaginatedCommentsForPostPromise]">
            <template #resolved>
                <div v-if="commentThreads?.length" class="mt-5">
                    <Thread 
                        v-for="(thread, index) in commentThreads" 
                        :key="thread.id"
                        :thread="thread"
                        :index="index"
                        view="main"
                        :bookclub-id="bookclub"
                        :replying-to-id="clubCommentSelectedForReply?.id"
                        :is-sub-thread="thread.depth && thread.depth > 0"
                        :parent-to-subthread="thread.replied_to && parentToSubthreadMap[thread.replied_to]"
                        @thread-selected="(thread) => clubCommentSelectedForReply = thread"
                    />
                </div>

                <div v-else class="mt-5 text-2xl fancy text-stone-600 text-center">
                    <!-- if there are no comments -->
                    🎉No comments yet🎉
                </div>
            </template>
            <template #loading>
                <div class="fancy loading gradient radius-sm py-5 text-center mb-5">Loading comments...</div>
            </template>
        </AsyncComponent>
    </div>

    <ErrorToast v-if="errorToastMessage" :message="errorToastMessage"/>
    <div class="mobile-menu-spacer"></div>
</template>
<script setup lang="ts">
// Vue
import {useRoute} from 'vue-router';
import { ref, computed } from 'vue';
// Services
import { urls, navRoutes } from '../../../../../services/urls';
import { db } from '../../../../../services/db';
import { PubSub } from '../../../../../services/pubsub';
// Stores
import { currentUser } from '../../../../../stores/currentUser';
// Component services
import { flattenThreads } from '@/components/feed/bookclubs/club/posts/comments/threads';
// Components
import ClubPost from './ClubPost.vue';
import AsyncComponent from '../../../partials/AsyncComponent.vue';
import ErrorToast from './../../../../../components/shared/ErrorToast.vue';
import ViewAwards from '../awards/ViewAwards.vue';
import Thread from './comments/Thread.vue';
import ClubPostCommentBar from './ClubPostCommentBar.vue';
import BackBtn from '@/components/feed/partials/back-btn.vue'

const route = useRoute();
const { user, bookclub, postId, commentId } = route.params;

let data = {
    post: {},
    error: {},
};

const clubCommentSelectedForReply = ref(null);

const commentData = ref({
    comments: [],
    errors: []
});

const pagination = ref({
    skip: 0,
    limit: 20,
});

const errorToastMessage = ref(null);

const getPostPromise = db.get(
    urls.concatQueryParams(
        urls.bookclubs.getClubFeed(bookclub), 
        { 'post_id': postId }
    ), 
    null, 
    false, 
    (res: PostResponse) => {
        data.post = res.posts;
    }, 
    (err: Error) => {
        data.error = err;
        console.error(err);
    }
);


let getPaginatedCommentsForPostPromise = db.get(
    urls.concatQueryParams(
        urls.reviews.getComments(postId), 
        { 'book_club_id': bookclub , ...pagination.value}
    ),
    null, 
    false, 
    (res) => {
        commentData.value.comments = res.data.comments;
    }, (err) => {
        commentData.value.errors = [err];
    }
);

const commentThreads = computed(() => {
    // We don't want to see replies to replies to replies on the main page.
    const MAX_DEPTH = 1;
    return flattenThreads(commentData.value.comments, MAX_DEPTH);    
});

const parentToSubthreadMap = computed(() => {
    const hashMap = <Object[Thread]>{};
    if (commentThreads.value.length) {
        commentThreads.value.forEach((thread) => {
            hashMap[thread.id] = thread;
        });
        return hashMap;
    }

    return {};
});

// ON pre success of posting a reply, 
// find the correct parent comment thread and add your comment to the end of the list.
// Different than commenting to a post which goes to the start of the list. 
PubSub.subscribe('footer-comment-pre-success-comment', (payload) => {
    const refComment = commentData.value.comments.find((comment) => comment.id === payload.commentId);

    if (refComment) {
        const reply = {
            text: payload.reply,
            username: currentUser.value.username,
            created_date: null, 
            num_replies: 0,
            liked_by_current_user: false,
            post_id: postId,
        };   
        refComment.replies.push(reply);
    } else {
        setTimeout(() => {
            errorToastMessage.value = 'Something weird happened 🤔';
        }, 1500);
    }
});
</script>
<style scoped>
.border { border: 1px solid var(--stone-300); } 
.post-wrap {
    padding: 20px 2rem;
  border: 1px solid var(--stone-300);
  border-left-width: 0;
  border-right-width: 0;
}
</style>
