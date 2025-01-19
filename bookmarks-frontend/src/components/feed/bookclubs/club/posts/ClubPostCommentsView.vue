<template>
    <!-- Load the post first. -->
    <AsyncComponent :promises="[getPostPromise]">
        <template #resolved>
            <div class="post-section">
                <ClubPost :post="data.post" :is-viewing-post="true"/>
                
                <CommentBar :post-id="data.post.id" @pre-success-comment="(comment) => addToComments(comment)" />
            </div>
        </template>
        <template #loading>
            <div class="fancy loading gradient">Loading...</div>
        </template>
    </AsyncComponent>
    
    <!-- Then load the comments as separate components -->
    <AsyncComponent :promises="[getPaginatedCommentsForPostPromise]">
        <template #resolved>
            <div v-if="commentData.comments?.length" class="mt-5">
                <ClubComment 
                    v-for="comment in commentData.comments" 
                    :key="comment.id" 
                    :comment-data="comment"
                />
            </div>

            <div v-else class="mt-5 text-2xl fancy text-stone-600 text-center">
                <!-- if there are no comments -->
                 🎉No comments yet🎉
            </div>
        </template>
        <template #loading>
            <div class="fancy loading gradient">Loading comments...</div>
        </template>
    </AsyncComponent>
</template>
<script setup>
import {useRoute, useRouter} from 'vue-router';
import { ref, onMounted, computed } from 'vue';
import { urls, navRoutes } from '../../../../../services/urls';
import { db } from '../../../../../services/db';
import ClubPost from './ClubPost.vue';
import AsyncComponent from '../../../partials/AsyncComponent.vue';
import CommentBar from './comments/CommentBar.vue';
import ClubComment from './comments/ClubComment.vue';
import { ws } from '../../../bookshelves/bookshelvesRtc';
import { currentUser } from './../../../../../stores/currentUser';
import { PubSub } from '../../../../../services/pubsub';

const route = useRoute();
const { user, bookclub, postId } = route.params;

let data = {
    post: {},
    error: {},
};

// onMounted(() => {
//     ws.createNewSocketConnection(urls.bookclubs.establishWebsocketConnectionForClub(bookclub))
// })

const commentData = ref({
    comments: [],
    errors: []
});

const pagination = ref({
    skip: 0,
    limit: 20,
});

const getPostPromise = db.get(
    urls.concatQueryParams(
        urls.bookclubs.getClubFeed(bookclub), 
        { 'post_id': postId }
    ), 
    null, 
    false, 
    (res) => {
        data.post = res.posts;
    }, 
    (err) => {
        data.error = err;
        console.error(err);
    }
);

const getPaginatedCommentsForPostPromise = db.get(
    urls.concatQueryParams(
        urls.reviews.getComments(postId), 
        { 'bookclub': bookclub }
    ),
    {...pagination.value}, 
    false, 
    (res) => {
        commentData.value.comments = res.data.comments;
    }, (err) => {
        commentData.errors = [err];
    }
);

function addToComments(message) {
    const comment = {
        text: message,
        username: currentUser.value.username,
        created_date: null,
        num_replies: 0,
        replies: [],
        liked_by_current_user: false,
        post_id: postId,
    }
    // See this at the top.
    commentData.value.comments.unshift({comment});
}

// ON pre success of posting a reply, 
// find the correct parent comment thread and add your comment to the end of the list.
// Different than commenting to a post which goes to the start of the list. 
PubSub.subscribe('footer-comment-pre-success-comment', (payload) => {
    const refComment = commentData.value.comments.find((comment) => comment.id === payload.commentId);
    const reply = {
        text: payload.reply,
        username: currentUser.value.username,
        created_date: null, 
        num_replies: 0,
        liked_by_current_user: false,
        post_id: postId,
    };

    refComment.value.replies.push(reply);
});

PubSub.subscribe('footer-comment-failure-comment', (payload) => {
    const refComment = commentData.value.comments.find((comment) => comment.id === payload.commentId);
    refComment.value.failedPosting = true;
});
</script>