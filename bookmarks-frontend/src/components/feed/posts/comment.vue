<template>
    <div class="my-3 comment">
        <p class="">{{ props.comment.text }}</p>
        <div class="comment-footer">
            <button 
                class=""
                type="button"
                @click="isReplying = !isReplying"
            >
                <IconComment/>
            </button>

            <button 
                class="ml-5 flex items-center justify-end"
                type="button"
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
                <IconSend />
            </button>
    </div>
    <Reply 
        v-for="(reply, index) in replies"
        :key="index"
        :reply="Object.entries(reply)[0][1]"
        :is-liked-by-current-user="reply.liked_by_current_user"
    />

    <button v-if="replies.length > 1" type="button" class="text-indigo-500 font-semibold underline">View more replies...</button>   

    
</template>
<script setup>
import Reply from './reply.vue';
import IconLike from '../../svg/icon-like.vue';
import IconComment from '../../svg/icon-comment.vue';
import IconPin from '../../svg/icon-pin.vue';

import { ref, computed } from 'vue';
import { urls } from '../../../services/urls';
import { db } from '../../../services/db';

const props = defineProps({
    comment: {
        type: Object,
        required: true,
    },
    isLikedByCurrentUser: {
        type: Boolean,
        required: true
    },
    replies: {
        type: Array,
        required: false,
    }
});

const reply = ref('');
const isReplying = ref(false);

const replies = computed(() => (props.replies));

async function postReply() {
    const data = {
        "post_id": props.comment.post_id,
        "text": reply.value,
        "pinned": false,
        "replied_to": props.comment.id,
    };

    await db.post(urls.reviews.createComment(), data, true).then((res) => {
        replies.value.push(res.data);
    })
}

</script>