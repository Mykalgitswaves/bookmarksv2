<template>
    <div class="reply comment">
        <p class="">{{ props.reply.comment.text }}</p>
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
                    v-if="props.reply?.comment.likes?.length" 
                    class="ml-2 text-indigo-500 italic"
                >
                    {{ props.reply?.comment.likes }}
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
</template>
<script setup>
import IconComment from '../../svg/icon-comment.vue';
import IconPin from '../../svg/icon-pin.vue';
import IconLike from '../../svg/icon-like.vue';
import { ref } from 'vue';

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

</script>