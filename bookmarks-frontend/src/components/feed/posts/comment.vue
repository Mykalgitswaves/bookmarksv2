<template>
    <div class="my-3 comment" :class="{'is-replying': isReplying, 'liked': (is_liked || comment.liked_by_current_user)}">
        <div class="comment-inner">
            <p class="comment-text">{{ props.comment.text }}</p>
            <div class="comment-footer">
                <button 
                    class=""
                    type="button"
                    @click="isReplying = !isReplying"
                >
                    <span v-if="!isReplying" class="flex items-center">
                        <IconComment />
                        <span class="text-sm ml-2 underline">reply</span>
                    </span>

                    <IconExit v-if="isReplying" />
                </button>

                <button 
                    class="ml-5 flex items-center justify-end"
                    type="button"
                    @click="likeComment()"
                >
                    <IconLike/>
                    <span 
                        class="ml-2 text-sm"
                        :class="{'text-indigo-500': is_liked}"    
                    >
                        {{ commentLikes }} 
                    </span>
                </button>

                <button 
                    v-if="props.comment.username === props.postUsername"
                    class="ml-5 flex items-center justify-end"
                    type="button"
                >
                    <IconPin/>
                    <span class="ml-1 text-sm">
                        pin
                    </span>
                </button>

                <button 
                    v-if="props.comment.posted_by_current_user"
                    class="ml-5"
                    type="button"
                    @click="deleteComment(props.comment.id)"
                >
                    <IconTrash/>
                </button>
            </div>
        </div>

        <transition-group name="content">
            <div v-if="isReplying" class="make-comments-container">
                <textarea 
                    class="make-comment-textarea"
                    type="text"
                    v-model="reply"
                    placeholder="Be nice, be thoughtful"    
                />

                <button
                    class="send-comment-btn" 
                    type="button"
                    @click="postReply()"
                >
                    <IconReply />
                </button>
            </div>
        </transition-group>
    </div>
    
    <Reply 
        v-for="(reply, index) in replies"
        :key="index"
        :reply="reply"
        :is-liked-by-current-user="reply.liked_by_current_user"
        @deleted="handleDelete($event)"
    />

    <button 
        v-if="props.comment.num_replies > 1 && !moreRepliesLoaded"
        type="button"
        class="text-indigo-500 font-semibold underline ml-5 mt-2 text-start"
        @click="fetchMoreReplies()"
    >
        View {{ num_replies - 1 }} more replies...
    </button>   
</template>
<script setup>
import Reply from './reply.vue';
import IconLike from '../../svg/icon-like.vue';
import IconComment from '../../svg/icon-comment.vue';
import IconPin from '../../svg/icon-pin.vue';
import IconReply from '../../svg/icon-reply.vue';
import IconExit from '../../svg/icon-exit.vue';
import IconTrash from '../../svg/icon-trash.vue';

import { ref, computed } from 'vue';
import { urls } from '../../../services/urls';
import { db } from '../../../services/db';

const props = defineProps({
    comment: {
        type: Object,
        required: true,
    },
    isLiked: {
        type: Boolean,
        required: false
    },
    replies: {
        type: Array,
        required: false,
    },
    postUsername: {
        type: String,
        required: false,
    },
    num_replies: {
        type: Number,
        required: true,
    },
    likes: {
        type: Number,
        required: true
    },
    pinned: {
        type: Boolean,
        required: false,
    }
});

const reply = ref('');
const isReplying = ref(false);
const is_liked = ref(props.comment.liked_by_current_user);
const replies = ref(props.replies ? props.replies.map((r) => r.comment) : []);
const moreRepliesLoaded = ref(false);
const commentLikes = ref(props.comment.likes);

const commentLikesFormatted = computed(() => {
    if(commentLikes.value === 1) {
        return `${commentLikes.value} like` 
    } else {
        return `${commentLikes.value} likes`
    }
})

const num_replies = ref(props.comment?.num_replies);
const emit = defineEmits();

async function postReply() {
    const data = {
        "post_id": props.comment.post_id,
        "text": reply.value,
        "pinned": false,
        "replied_to": props.comment.id,
    };

    if(reply.value.length) {
        await db.post(urls.reviews.createComment(), data).then((res) => {
            replies.value?.unshift(res.data);
            isReplying.value = false;
            num_replies.value += 1;
        });
    };
};

async function likeComment() {
    if(is_liked.value === false) {
        is_liked.value = true;
        commentLikes.value += 1
        await db.put(urls.reviews.likeComment(props.comment.id));
    } else {
        is_liked.value = false;
        commentLikes.value -= 1;
        await db.put(urls.reviews.unlikeComment(props.comment.id))    
    }
};

async function fetchMoreReplies() { 
    await db.get(urls.reviews.getMoreComments(props.comment.id)).then((res) => {
        replies.value = res.data.slice(1, res.data.length + 1);
        moreRepliesLoaded.value = true;
    })
}

async function deleteComment(comment_id) {
    await db.put(urls.reviews.deleteComment(comment_id)).then(() => {
        emit('comment-deleted', comment_id)
    })
}

function handleDelete(event) {
    replies.value = replies.value.filter((r) => {
        r.id !== event
    });
}

async function pinComment(comment_id, post_id) {
    
}

</script>