<template>
    <!-- Load the post first. -->
    <AsyncComponent :promises="[getPostPromise]">
        <template #resolved>
            <ClubPost :post="data.post" :is-viewing-post="true"/>

            <CommentBar :post-id="data.post.id" @comment-created="(comment) => addToComments(comment)"/>
        </template>
        <template #loading>
            <div class="fancy loading gradient">Loading...</div>
        </template>
    </AsyncComponent>
    
    <!-- Then load the comments as separate components -->
    <AsyncComponent :promises="[getPaginatedCommentsForPostPromise]">
        <template #resolved>
            <div v-if="commentData.comments?.length" class="club-comments">
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
import { ref } from 'vue';
import { urls, navRoutes } from '../../../../../services/urls';
import { db } from '../../../../../services/db';
import ClubPost from './ClubPost.vue';
import AsyncComponent from '../../../partials/AsyncComponent.vue';
import CommentBar from './comments/CommentBar.vue';
import ClubComment from './comments/ClubComment.vue';

const route = useRoute();
const { user, bookclub, postId } = route.params;
let data = {
    post: {},
    error: {},
};

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
        commentData.value.comments = res.data.comments
    }, (err) => {
        commentData.errors = [err];
    });

function addToComments(comment) {
    commentData.value.comments.push(comment);
}
</script>