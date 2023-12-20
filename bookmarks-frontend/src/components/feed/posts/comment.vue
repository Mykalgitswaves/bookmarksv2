<template>
    <p class="comment-username">{{ props.comment.username }}:</p>

    <div 
        class="my-3 comment" 
        :class="{
            'is-replying': isReplying,
            'liked': (is_liked || comment.liked_by_current_user),
            'pinned': isPinned
        }"
    >

        <button 
            v-if="isPinned"
            type="button" 
            class="pinned-comment-btn"
            :disabled="!isOpOfPost" 
            @click="pinComment()"
        >
            <IconPin/>
        </button>  

        <div class="comment-inner">
            <p class="comment-text">{{ props.comment.text }}</p>
        </div>
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
                :disabled="liking"
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
                v-if="isOpOfComment && !isOpOfPost"
                type="button"
                class="ml-5"
                @click="deleteComment(props.comment.id)"
            >
                <IconTrash/>
            </button>

            <button
                v-if="isOpOfPost" 
                class="ml-5 "
                type="button"
                @click="flyoutToggle = !flyoutToggle"
            >
                <IconMore/>
            </button>
            
            <div
                :class="{'popout-comment shadow-lg': flyoutToggle}"
            >
                <div v-if="flyoutToggle" class="flyout">
                    <button 
                        type="button"
                        @click="pinComment(); flyoutToggle = false"
                    >
                        <IconPin/>
                        <span class="ml-2" v-if="!isPinned">
                            pin
                        </span>
                        <span class="ml-2" v-else>
                            unpin
                        </span>
                    </button>

                    <button 
                        v-if="props.comment.posted_by_current_user"
                        type="button"
                        :disabled="deleting"
                        @click="deleteComment(props.comment.id)"
                    >
                        <IconTrash/>
                        <span class="ml-2">
                            {{ deleteStatus }}
                        </span>
                    </button>
                </div>

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
        :opUserUuid="props.opUserUuid"
        @deleted="($event) => (replies = replies.filter((r) => (r.id !== $event)))"
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
import IconMore from '../../svg/icon-more.vue';
import { useRoute } from 'vue-router';
import { ref } from 'vue';
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
    },
    opUserUuid: {
        type: String,
        required: true,
    },
});

const reply = ref('');
const isReplying = ref(false);
const is_liked = ref(props.comment.liked_by_current_user);
const replies = ref(props.replies ? props.replies.map((r) => r.comment) : []);
const isPinned = ref(props.comment.pinned);
const moreRepliesLoaded = ref(false);
const commentLikes = ref(props.comment.likes);
const flyoutToggle = ref(false);
const route = useRoute();
const { user } = route.params;
const num_replies = ref(props.comment?.num_replies);

// Limit btns for liking and deleting and replying by adding disabled states.
const deleteStatus = ref('delete');
const deleting = ref(false);

const liking = ref(false);

const emit = defineEmits(['comment-deleted', 'comment-pinned', 'comment-unpinned']);

let isOpOfPost;
let isOpOfComment;

if(user === props.opUserUuid){
    isOpOfPost = true 
} else {
    isOpOfPost = false;
}

if(user === props.comment.user_id) {
    isOpOfComment = true; 
} else {
    isOpOfComment = false;
}

async function postReply() {
    const data = {
        "post_id": props.comment.post_id,
        "text": reply.value,
        "pinned": false,
        "replied_to": props.comment.id,
    };

    if(reply.value.length) {
        await db.post(urls.reviews.createComment(), data).then((res) => {
            // replies go to bottom of list?
            replies.value?.push(res.data);
            isReplying.value = false;
            num_replies.value += 1;
            //default to blank reply in comment.
            reply.value = '';
        });
    };
};

async function likeComment() {
    liking.value = true;
    if(is_liked.value === false) {
        is_liked.value = true;
        commentLikes.value += 1
        await db.put(urls.reviews.likeComment(props.comment.id)).then(() => {
            liking.value = false;
        });
    } else {
        is_liked.value = false;
        commentLikes.value -= 1;
        await db.put(urls.reviews.unlikeComment(props.comment.id)).then(() => {
            liking.value = true;
        })    
    }
};

async function fetchMoreReplies() { 
    await db.get(urls.reviews.getMoreComments(props.comment.id)).then((res) => {

        replies.value = res.data;
        moreRepliesLoaded.value = true;
    })
}

async function deleteComment(comment_id) {
    deleting.value = true;
    deleteStatus.value = 'deleting';
    
    await db.put(urls.reviews.deleteComment(comment_id)).then(() => {
        deleting.value = false;
        deleteStatus.value = 'deleted';
        emit('comment-deleted', comment_id)
    })
}

async function pinComment() {
    if(!isPinned.value) {
        isPinned.value = true;
        await db.put(urls.reviews.pinComment(props.comment.id, props.comment.post_id)).then(() => {
            emit('comment-pinned', props.comment.id)
        })
    } else {
        isPinned.value = false
        await db.put(urls.reviews.unpinComment(props.comment.id, props.comment.post_id)).then(() => {
            emit('comment-unpinned', props.comment.id)
        })
    }
}

</script>