<template>
    <div class="reply comment">
        <div class="comment-inner">
            <p v-if="props.reply.comment">{{ props.reply?.comment?.text }}</p>
            <p v-if="props.reply.text">{{ props.reply?.text }}</p>

            <div class="comment-footer">
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

                <button
                    class="ml-5 flex items-center justify-end text-red-600"
                    type="button"
                    role="delete"
                    @click="deleteReply(props.reply.id)"
                >
                    <IconTrash/>
                </button>
            </div>
        </div>
    </div>
</template>
<script setup>
import IconPin from '../../svg/icon-pin.vue';
import IconLike from '../../svg/icon-like.vue';
import IconTrash from '../../svg/icon-trash.vue';

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
});

console.log(props);

const emit = defineEmits();

async function deleteReply(post_id) { 
    await db.put(urls.reviews.deleteComment(post_id), null).then(() => {
        emit('deleted', post_id);
    });
}
</script>