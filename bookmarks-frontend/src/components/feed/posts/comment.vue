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
                    v-if="props.comment.username === props.postUsername"
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
        :reply="Object.values(reply)[0]"
        :is-liked-by-current-user="reply.liked_by_current_user"
        @deleted="handleDelete($event)"
    />

    <button 
        v-if="replies.length > 0 && !moreRepliesLoaded"
        type="button"
        class="text-indigo-500 font-semibold underline ml-5 mt-2 justify-self-start"
        @click="fetchMoreReplies()"
    >
        View more replies...
    </button>   

    <div v-if="moreRepliesLoaded" class="comments-wrapper">
        <Reply 
            v-for="(reply, index) in moreReplies"
            :key="index"
            :reply="reply"
            :is-liked-by-current-user="reply.liked_by_current_user"
            @deleted="handleDelete($event)"
        />
    </div>
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
});

console.log(props)

const reply = ref('');
const isReplying = ref(false);
const is_liked = ref(props.isLiked);
const replies = ref(props.replies);
const moreRepliesLoaded = ref(false);
const moreReplies = ref([]);
const emit = defineEmits();

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
        moreReplies.value = res.data;
        moreRepliesLoaded.value = true;
    })
}

async function deleteComment(comment_id) {
    await db.put(urls.reviews.deleteComment(comment_id), null, true).then(() => {
        emit('comment-deleted', comment_id)
    })
}


function handleDelete(event) {
    moreReplies.value = moreReplies.value.filter((r) => r !== event)
}

</script>