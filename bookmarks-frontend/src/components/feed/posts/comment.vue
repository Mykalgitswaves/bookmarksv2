<template>
    <div class="my-3 comment" :class="{'is-replying': isReplying, 'liked': is_liked}">
        <div class="comment-inner">
            <p class="">{{ props.comment.text }}</p>
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
                    @click="is_liked ? unlikeComment() : likeComment()"
                >
                    <IconLike/>
                    <span
                        v-if="props.comment?.likes?.length" 
                        class="ml-2 text-indigo-500 italic"
                    >
                        {{ props.comment?.likes }}
                    </span>
                </button>

                <button 
                    v-if="isOp"
                    class="ml-5 flex items-center justify-end"
                    type="button"
                >
                    <IconPin/>
                    <span
                        v-if="props.comment?.likes?.length" 
                        class="ml-2 text-indigo-500 italic"
                    >
                        {{ props.comment?.likes }}
                    </span>
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
        :reply="Object.entries(reply)[0][1]"
        :is-liked-by-current-user="reply.liked_by_current_user"
        @reply-posted="($event) => replies.push($event)"
    />

    <button 
        v-if="replies.length > 0 && !moreRepliesLoaded"
        type="button"
        class="text-indigo-500 font-semibold underline ml-5 mt-2"
        @click="fetchMoreReplies()"
    >
        View more replies...
    </button>   
    
</template>
<script setup>
import Reply from './reply.vue';
import IconLike from '../../svg/icon-like.vue';
import IconComment from '../../svg/icon-comment.vue';
import IconPin from '../../svg/icon-pin.vue';
import IconReply from '../../svg/icon-reply.vue';
import IconExit from '../../svg/icon-exit.vue';

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
        required: true
    },
    replies: {
        type: Array,
        required: false,
    }
});

console.log(props.isLiked)

const reply = ref('');
const isReplying = ref(false);
const is_liked = ref(props.isLiked);
const replies = ref(props.replies);
const moreRepliesLoaded = ref(false);

async function postReply() {
    const data = {
        "post_id": props.comment.post_id,
        "text": reply.value,
        "pinned": false,
        "replied_to": props.comment.id,
    };

    if(reply.value.length) {
        await db.post(urls.reviews.createComment(), data, true).then((res) => {
            replies.value.push(res.data);
        });
    };
};

async function likeComment() {
    is_liked.value = true;
    await db.put(urls.reviews.likeComment(props.comment.id));
};

async function unlikeComment(){
    is_liked.value = false;
    await db.put(urls.reviews.unlikeComment(props.comment.id))
}

async function fetchMoreReplies() { 
    await db.get(urls.reviews.getMoreComments(props.comment.id)).then((res) => {
        console.log(res)
        moreRepliesLoaded.value = true;
    })
}

</script>