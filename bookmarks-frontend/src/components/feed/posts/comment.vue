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
                @click="postComment()"
            >
                <IconSend />
            </button>
        </div>
</template>
<script setup>
import IconLike from '../../svg/icon-like.vue';
import IconComment from '../../svg/icon-comment.vue';
import IconPin from '../../svg/icon-pin.vue'
import { ref } from 'vue';
import { useRoute } from 'vue-router'

const props = defineProps({
    comment: {
        type: Object,
        required: true,
    },
    isLikedByCurrentUser: {
        type: Boolean,
        required: true
    }
});


const reply = ref('');
const isReplying = ref(false);
const route = useRoute();
const isOp = () => {
    const op = route.params
}
</script>
<style scoped>
.comment {
    display: block;
    padding: 14px 2.25rem;
    border-radius: 8px;
    border: solid 1px rgb(238 242 255);
    transition-duration: 250ms;
    transition-timing-function: ease;
}

.comment:hover {
    border-color: #c7d2fe;
}

.comment-footer {
    display: flex;
    align-items: center;
    justify-content: end;
    margin-top: .5em;
}
</style>