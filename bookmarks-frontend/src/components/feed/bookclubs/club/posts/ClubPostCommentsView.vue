<template>
    <!-- Load the post first. -->
    <AsyncComponent :promises="[getPostPromise]">
        <template #resolved>
            <ClubPost :post="data.post" :is-viewing-post="true"/>

            <ViewAwards/>

            <div 
                style="margin-top: 20px" 
                :class="{'scrolled-below-post': isScrollPastCommentBar && clubCommentSelectedForReply}"
                ref="commentBarRef"
            >   
                <!-- If you have selected a comment to reply to then do that shit -->
                    <span v-if="clubCommentSelectedForReply" class="text-sm ml-5 mb-2 block">replying to
                    <span class="text-indigo-500 fancy">{{ clubCommentSelectedForReply.comment?.username }}'s'</span>
                    comment
                </span>

                <div :class="{'comment-bar-section': clubCommentSelectedForReply}">
                    <CommentBar 
                        :post-id="data.post.id"
                        :comment="clubCommentSelectedForReply" 
                        @pre-success-comment="(comment) => addToComments(comment)" 
                    />

                    <button 
                        v-if="clubCommentSelectedForReply"
                        type="button" 
                        class="btn btn-tiny btn-red mb-2"
                        @click="clubCommentSelectedForReply = null"
                    >
                        <IconExit/>
                    </button>
                </div>
            </div>
        </template>
        <template #loading>
            <div class="fancy loading gradient radius-sm py-5 text-center mb-5">Loading post...</div>
        </template>
    </AsyncComponent>
    
    <!-- Then load the comments as separate components -->
    <AsyncComponent :promises="[getPaginatedCommentsForPostPromise]">
        <template #resolved>
            <div v-if="commentData.comments?.length" class="mt-5">
                <ClubComment 
                    v-for="(comment, index) in commentData.comments" 
                    :key="comment.id" 
                    :index="index"
                    :comment-data="comment"
                    :is-replying-to-key="clubCommentSelectedForReply?.id"
                    @comment-selected="(comment) => { clubCommentSelectedForReply = comment; console.log(comment)}"
                />

                <!-- <ClubCommentV2 
                    v-for="(comment, index) in flatComments" 
                    :key="comment.id"
                    :comment-data="comment"
                    :index="index"
                    :max-depth-of-thread="maxDepth"
                    :comment-depth="index"
                    :sub-thread-collapsed="false"
                /> -->
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

    <ErrorToast v-if="errorToastMessage" :message="errorToastMessage"/>
</template>
<script setup>
import {useRoute, useRouter} from 'vue-router';
import { ref, onMounted, computed } from 'vue';
import { urls, navRoutes } from '../../../../../services/urls';
import { helpersCtrl, generateUUID } from '../../../../../services/helpers';
import { db } from '../../../../../services/db';
import { CommentService } from './comments/comment'
import ClubPost from './ClubPost.vue';
import AsyncComponent from '../../../partials/AsyncComponent.vue';
import CommentBar from './comments/CommentBar.vue';
import ClubComment from './comments/ClubComment.vue';
// testing a second one.
import ClubCommentV2 from './comments/ClubCommentV2.vue';
import { ws } from '../../../bookshelves/bookshelvesRtc';
import { currentUser } from './../../../../../stores/currentUser';
import { PubSub } from '../../../../../services/pubsub';
import ErrorToast from './../../../../../components/shared/ErrorToast.vue';
import ViewAwards from '../awards/ViewAwards.vue';
import IconExit from '../../../../svg/icon-exit.vue';

const route = useRoute();
const { user, bookclub, postId } = route.params;

let data = {
    post: {},
    error: {},
};

const { debounce } = helpersCtrl;

// #TODO: @michael do this later.
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

const errorToastMessage = ref(null);

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
        { 'book_club_id': bookclub , ...pagination.value}
    ),
    null, 
    false, 
    (res) => {
        commentData.value.comments = res.data.comments;
    }, (err) => {
        commentData.errors = [err];
    }
);


function addToComments(message) {
    const comment = {
        id: generateUUID(), // In memory uuid to avoid collisions when possible.
        text: message,
        username: currentUser.value.username,
        created_date: null,
        num_replies: 0,
        replies: [],
        liked_by_current_user: false,
        post_id: postId,
    }

    // If you are replying to a specific comment push to the bottom of the replies of that comment.
    if (clubCommentSelectedForReply.value) {
        commentData.value.comments[clubCommentSelectedForReply.value.index]?.replies.push({comment: comment})
        // 
    } else {
        commentData.value.comments.unshift({comment});
    }
}

// ON pre success of posting a reply, 
// find the correct parent comment thread and add your comment to the end of the list.
// Different than commenting to a post which goes to the start of the list. 
PubSub.subscribe('footer-comment-pre-success-comment', (payload) => {
    const refComment = commentData.value.comments.find((comment) => comment.id === payload.commentId);
    
    console.log(refComment)

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

PubSub.subscribe('footer-comment-failure-comment', (payload) => {
    const refComment = commentData.value.comments.find((comment) => comment.id === payload.commentId);
    refComment.value.failedPosting = true;
});


const isScrollPastCommentBar = ref(false);
const commentBarRef = ref(null);
const clubCommentSelectedForReply = ref(null);
// This is all so we can have some smarter comment bar on desktop.
// probably bad component design on my part though.
onMounted(() => {
    const initialScrollHeight = window.scrollY;
    
    function handleScrollEvent() {
        console.log('called')
        
            console.log('made it apst first check')
            // im prefixing a dom element with $. 
            // All that means is that its the actual dom element 
            // Im adding an event listener to. CHat im just using slang.
            const $commentBar = commentBarRef.value;
            
            if ($commentBar) {
                const { bottom } = $commentBar.getBoundingClientRect();
                const isCurrentlyPastBottom = !!(bottom < 0);
                // if the value has changed since you last set it and the currnt scroll y is greater than the initial scroll y height.
                 // Only check if the user has scrolled past the initial scroll height

                if (initialScrollHeight + 20 <= window.scrollY) {
                    // Set to true only if it was previously false
                    if (!isScrollPastCommentBar.value && isCurrentlyPastBottom) {
                        isScrollPastCommentBar.value = true;
                        console.log('Scrolled past the comment bar');
                    }
                } else {
                    // If scrolling back up and the comment bar is visible, set to false
                    if (isScrollPastCommentBar.value && !isCurrentlyPastBottom) {
                        isScrollPastCommentBar.value = false;
                        console.log('Scrolled back up to the comment bar');
                        // if you haven't figured out what you want to say already, nock it off and make em reselect.
                        clubCommentSelectedForReply.value = null;
                    }
                }
            }
    }

    const debouncedScrollEvent = debounce(handleScrollEvent, 250, false);
    window.addEventListener('scroll', debouncedScrollEvent, {passive: true});
});
</script>
<style scoped>
@starting-style {
    .scrolled-below-post {
        opacity: 0;
    }
}

.scrolled-below-post {
    position: fixed;
    bottom: 20px;
    width: 90vw;
    max-width: 768px;
    z-index: 99999;
    background-color: var(--surface-primary);
    box-shadow: var(--shadow-lg);
    border-radius: var(--radius-md);
    padding: 20px;
    transition: all 250ms ease-in-out;
}
</style>