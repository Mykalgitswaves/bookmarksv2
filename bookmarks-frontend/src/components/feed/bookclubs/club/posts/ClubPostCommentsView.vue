<template>
    <div class="border">
        <BackBtn :back-fn="() => $router.push(navRoutes.toBookClubFeed(user, bookclub))"/>
        <!-- Load the post first. -->
        <AsyncComponent :promises="[getPostPromise]">
            <template #resolved>
                <div class="post-wrap">
                    <ClubPost :post="postData.post" :is-viewing-post="true"/>
                    
                    <ViewAwards/>
                </div>

                <ClubPostCommentBar 
                    :post-id="postData.post?.id" 
                    :comment="clubCommentSelectedForReply" 
                    @stop-commenting="clubCommentSelectedForReply = null"
                    @comment-created="(thread) => addThreadToComments(thread)"    
                />
            </template>
            <template #loading>
                <div class="fancy loading gradient radius-sm py-5 text-center mb-5">Loading post...</div>
            </template>
        </AsyncComponent>
        

        <!-- Pinned, allows us to rerender on pin of a comment. -->
        <!-- <AsyncComponent 
            :promise-factory="getPaginatedCommentsForPostPromiseFactory" 
            :subscription-key="PINNED_COMMENTS_SUBSCRIPTION_KEY"
        >
            <template #resolved>
                <div>
                    <Thread 
                        class="mb-3 pinned"
                        v-for="(thread, index) in pinnedCommentThreads"
                        :key="index"
                        :index="index"
                        view="main"
                        :post="postData?.post"
                        :bookclub-id="bookclub"
                        :replying-to-id="clubCommentSelectedForReply?.id"
                        :is-sub-thread="thread.depth && thread.depth > 0"
                        :parent-to-subthread="thread.replied_to && parentToSubthreadMap[thread.replied_to]"
                        @thread-selected="(thread) => clubCommentSelectedForReply = thread"
                        @unpinned="([index, thread]) => moveThreadToUnpinned(index, thread)"
                    />
                </div>
            </template>
            <template #loading>

            </template>
        </AsyncComponent> -->


        <!-- Then load the comments as separate components -->
        <AsyncComponent :promises="[getPaginatedCommentsForPostPromiseFactory()]">
            <template #resolved>
                <div v-if="pinnedCommentThreads" class="mt-5">
                    <Thread 
                        class="mb-3 pinned"
                        v-for="(thread, index) in pinnedCommentThreads"
                        :key="thread.id"
                        :thread="thread"
                        :index="index"
                        view="main"
                        :pinned="true"
                        :post="postData?.post"
                        :bookclub-id="bookclub"
                        :replying-to-id="clubCommentSelectedForReply?.id"
                        :is-sub-thread="thread.depth && thread.depth > 0"
                        :parent-to-subthread="thread.replied_to && parentToSubthreadMap[thread.replied_to]"
                        @thread-selected="(thread) => clubCommentSelectedForReply = thread"
                        @pre-success-thread-unpinned="([index, thread]) => moveThreadToUnpinned(index, thread)"
                        @post-success-thread-unpinned="() => console.log('dude you did it')"
                        @error-unpinning-thread="() => console.log('we should probably use test')"
                    />
                </div>

                <div v-if="commentThreads" class="mt-5">
                    <Thread 
                        v-for="(thread, index) in commentThreads" 
                        class="mb-3"
                        :class="{'border-t-light': thread.depth === 0}"
                        :key="thread.id"
                        :thread="thread"
                        :index="index"
                        view="main"
                        :post="postData?.post"
                        :bookclub-id="bookclub"
                        :replying-to-id="clubCommentSelectedForReply?.id"
                        :is-sub-thread="thread.depth && thread.depth > 0"
                        :parent-to-subthread="thread.replied_to && parentToSubthreadMap[thread.replied_to]"
                        @thread-selected="(thread) => clubCommentSelectedForReply = thread"
                        @pre-success-thread-pinned="(([index, thread]) => moveThreadToPinned(index, thread))"
                        @post-success-thread-pinned="() => console.log('yo dude')"
                        @error-pinning-thread="() => console.log('we should probably use test')"
                    />
                </div>

                <div v-else class="mt-5 text-2xl fancy text-stone-600 text-center pb-5">
                    <!-- if there are no comments -->
                    No comments yet
                </div>
            </template>
            <template #loading>
                <div class="fancy loading gradient radius-sm py-5 text-center mb-5 pb-5">Loading comments...</div>
            </template>
        </AsyncComponent>
    </div>

    <ErrorToast v-if="errorToastMessage" :message="errorToastMessage"/>
    <div class="mobile-menu-spacer"></div>
</template>
<script setup lang="ts">
// Vue
import { ref, computed, defineAsyncComponent } from 'vue';
import { useRoute } from 'vue-router';
// Services
import { urls, navRoutes } from '../../../../../services/urls';
import { db } from '../../../../../services/db';
import { PubSub } from '../../../../../services/pubsub';
// Component services
import { flattenThreads, Thread as ThreadInterface } from '@/components/feed/bookclubs/club/posts/comments/threads';

// Components
import BackBtn from '@/components/feed/partials/back-btn.vue';
import AsyncComponent from '../../../partials/AsyncComponent.vue';
import ClubPost from './ClubPost.vue';
import ClubPostCommentBar from './ClubPostCommentBar.vue';
import ErrorToast from './../../../../../components/shared/ErrorToast.vue';

// Asyncs
const ViewAwards = defineAsyncComponent(() => import('../awards/ViewAwards.vue'));
const Thread = defineAsyncComponent(() => import('./comments/Thread.vue'));

const route = useRoute();
const { user, bookclub, postId, commentId } = route.params;

const postData = ref({
    post: {},
    error: {},
});

const clubCommentSelectedForReply = ref(null);

const commentData = ref({
    comments: [] as ThreadInterface[],
    pinnedComments: [] as ThreadInterface[],
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
        postData.value.post = res.posts;
    }, 
    (err: Error) => {
        postData.value.error = err;
        console.error(err);
    }
);

/**
 * @THREADS
 */

const getPaginatedCommentsForPostPromiseFactory = () => (db.get(
    urls.concatQueryParams(
        urls.reviews.getComments(postId), 
        { 'book_club_id': bookclub , ...pagination.value}
    ),
    null, 
    false, 
    (res) => {
        commentData.value.comments = res.data.comments;
        commentData.value.pinnedComments = res.data.pinned_comments;
    }, (err) => {
        commentData.value.errors = [err];
    },
));

// Some js trickery, we want to recomputed commentThreads whenever we add a new reply to a thread.
// Computed reruns when a reactive dept is changed, so this little hack helps us make sure the 
// comments are appearing after they are posted. 
// ( Something about how vue doesn't know when deeply nested state has changed inside computed. Probably being shallow watched )
let triggerCommentRerender = Symbol('huh?');

function addThreadToComments(thread:any) {
    if (clubCommentSelectedForReply) {
        // find the thread to add to the replies of
        const { id } = clubCommentSelectedForReply.value;
        const commentToAddThreadTo = commentData.value.comments.find((comment) => comment.id === id);
        // Question - will this actually rerender?
        if (commentToAddThreadTo) {
            thread.depth = 1;
            commentToAddThreadTo.thread.unshift(thread);
            triggerCommentRerender = Symbol('Dude');
            // do something to trigger the computed comment again to flatten everything based on whats in memory
            return;
        };
    }

    commentData.value.comments.unshift(thread);
};

// We don't want to see replies to replies to replies on the main page.
const MAX_THREAD_DEPTH = 1;

// Computed functions that render on load, maybe these don't need to be computed - #TODO: think about not computed. 
// Thought about it, they still do. 
const commentThreads = computed(() => {
    // Force refresh for computed func.
    triggerCommentRerender;
    if (!commentData.value.comments.length) {
        return []
    }
    return flattenThreads(commentData.value.comments, MAX_THREAD_DEPTH);    
});

// Used to trigger refreshes after you pin a comment.
const PINNED_COMMENTS_SUBSCRIPTION_KEY = `load-pinned-comments-bookclub-${bookclub}`;

const pinnedCommentThreads = computed(() => {
    triggerCommentRerender;
    if (!commentData.value.pinnedComments.length) {
        return [];
    }

    return flattenThreads(commentData.value.pinnedComments, MAX_THREAD_DEPTH);
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

// UI functions for moving threads to pinned
function moveThreadToPinned(index: Number, emittedThread: any) {
    commentData.value.comments = commentData.value.comments.filter(
        (thread: any, i:Number) => i !== index);

    commentData.value.pinnedComments.push(emittedThread);
    // triggerCommentRerender = Symbol('pinned');
};

function moveThreadToUnpinned(index: Number, emittedThread: any) {
    // Start by removing emitted thread from pinned.
    commentData.value.pinnedComments = commentData.value.pinnedComments.filter(
        (thread: any, i: Number) => i !== index);

    commentData.value.comments.push(emittedThread);
    // triggerCommentRerender = Symbol('unpinned');
}
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
