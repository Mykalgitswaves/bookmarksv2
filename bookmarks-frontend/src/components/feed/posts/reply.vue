<template>
    <div class="reply comment" 
    :class="{
        'liked': is_liked,
        'op': props.reply?.posted_by_current_user 
    }">
        <div class="comment-inner">
            <p v-if="props.reply">{{ props.reply?.text }}</p>

            <div class="comment-footer">
                <button 
                    class="ml-5 flex items-center justify-end"
                    type="button"
                    @click="likeComment()"
                >
                    <IconLike/>
                    <span class="ml-2">
                        {{ commentLikesFormatted }}
                    </span>
                </button>

                <button 
                    v-if="isOp"
                    class="ml-5 flex items-center justify-end"
                    type="button"
                >
                    <IconPin/>
                    <span
                        v-if="props.reply?.likes" 
                        class="ml-2 text-indigo-500 italic"
                    >
                        {{ props.reply?.likes }}
                    </span>
                </button>

                <button
                    class="ml-5 flex items-center justify-end text-red-600"
                    type="button"
                    role="delete"
                    @click="deleteReply(props.reply?.id)"
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

import { ref, computed } from 'vue';
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
const is_liked = ref(props.reply?.liked_by_current_user);
const commentLikes = ref(props.reply?.likes)
const emit = defineEmits();

const commentLikesFormatted = computed(() => {
    if(commentLikes.value === 1) {
        return `${commentLikes.value} like` 
    } else {
        return `${commentLikes.value} likes`
    }
})

async function likeComment() {
    if(is_liked.value === false){
        is_liked.value = true;
        commentLikes.value += 1
        await db.put(urls.reviews.likeComment(props.reply?.id), null, true);
    } else {
        is_liked.value = false;
        commentLikes.value -= 1
        await db.put(urls.reviews.unlikeComment(props.reply?.id), null, true);
    }
}

async function deleteReply(post_id) { 
    await db.put(urls.reviews.deleteComment(post_id), null).then(() => {
        emit('deleted', post_id);
    });
}
</script>