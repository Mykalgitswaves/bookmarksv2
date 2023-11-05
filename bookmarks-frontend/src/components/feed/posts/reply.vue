<template>
    <div class="reply comment">
        <div class="comment-inner">
            <p v-if="props.reply.comment">{{ props.reply?.comment?.text }}</p>
            <p v-if="props.reply.text">{{ props.reply?.text }}</p>

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
                >
                    <IconLike/>
                    <span
                        v-if="props.reply?.comment?.likes?.length" 
                        class="ml-2 text-indigo-500 italic"
                    >
                        {{ props.reply?.comment?.likes }}
                    </span>
                </button>

                <button 
                    v-if="isOp"
                    class="ml-5 flex items-center justify-end"
                    type="button"
                >
                    <IconPin/>
                    <span
                        v-if="props.reply?.comment.likes?.length" 
                        class="ml-2 text-indigo-500 italic"
                    >
                        {{ props.reply?.comment.likes }}
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
</template>
<script setup>
import IconComment from '../../svg/icon-comment.vue';
import IconPin from '../../svg/icon-pin.vue';
import IconLike from '../../svg/icon-like.vue';
import IconReply from '../../svg/icon-reply.vue';
import IconExit from '../../svg/icon-exit.vue';

import { ref } from 'vue';
import { db } from '../../../services/db';
import { urls } from '../../../services/urls';

const props = defineProps({
    reply: {
        type: Object,
        required: true
    },
    isLikedByCurrentUser: {
        type: Boolean,
        default: false,
    }
})

const isReplying = ref(false);
const reply = ref('');
const emit = defineEmits();

async function postReply() {
    const data = {
        "post_id": props.reply.comment.post_id,
        "text": reply.value,
        "pinned": false,
        "replied_to": props.reply.comment.replied_to,
    };

    if (reply.value.length) {
        await db.post(urls.reviews.createComment(), data, true).then((res) => {
            emit('reply-posted', res.data);
        });
    };
}
</script>