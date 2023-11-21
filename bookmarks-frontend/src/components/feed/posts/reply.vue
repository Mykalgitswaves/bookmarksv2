<template>
    <p class="comment-username reply">{{ props.reply.username }}:</p>
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
                    v-if="isOpOfPost || isOpOfComment"
                    class="ml-5 flex items-center justify-end text-red-600"
                    type="button"
                    role="delete"
                    @click="deleteReply()"
                >
                    <IconTrash/>
                </button>
            </div>
        </div>
    </div>
</template>
<script setup>
// import IconPin from '../../svg/icon-pin.vue';
import IconLike from '../../svg/icon-like.vue';
import IconTrash from '../../svg/icon-trash.vue';

import { ref, computed } from 'vue';
import { useRoute } from 'vue-router';
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
    },
    opUserUuid: {
        type: String,
        required: true,
    }
});

const route = useRoute()
const { user } = route.params;

let isOpOfPost;
let isOpOfComment;

if(user === props.opUserUuid){
    isOpOfPost = true 
} else {
    isOpOfPost = false;
}

if(user === props.reply.user_id) {
    isOpOfComment = true; 
} else {
    isOpOfComment = false;
}

const is_liked = ref(props.reply?.liked_by_current_user);
const commentLikes = ref(props.reply?.likes);
const emit = defineEmits(['deleted']);

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

async function deleteReply() { 
    emit('deleted', props.reply.id);
    await db.put(urls.reviews.deleteComment(props.reply.id), null, true);
}
</script>