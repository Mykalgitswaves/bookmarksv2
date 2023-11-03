<template>
    <div class="flex content-center px-2">
        <div class="make-comments-container">
            <textarea 
                class="make-comment-textarea"
                type="text"
                v-model="comment"
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
    </div>
    <div v-if="!props.comments.length">
        <p class="text-center text-2xl text-indigo-500 font-bold">Pretty quiet here... 🦗<span class="block text-lg font-medium text-slate-600">Get the conversation started with your opinion</span></p>
    </div>

    <div v-else>
        <Comment
            v-for="(comment,index) in comments"
            :key="index"
            :comment="comment"
        />
    </div>
</template>
<script setup>
import { db } from '../../../services/db';
import { urls } from '../../../services/urls';
import { ref, computed } from 'vue';
import IconSend from '../../svg/icon-send.vue';
import Comment from './comment.vue';

const props = defineProps({
    comments: {
        type: Array,
        required: false,
    },
    postId: {
        type: String,
        required: true,
    }
});

const comment = ref('')
const comments = computed(() => props.comments);
const replied_to = ref(null)

async function postComment(){
    const data = {
        "post_id": props.postId,
        "text": comment.value,
        "pinned": false,
        "replied_to": replied_to.value,
    }
    await db.post(urls.reviews.createComment(), data, true).then((res) => comments.value.push(res.data))
}
</script>

<style scoped>
    .send-comment-btn {
        padding: 12px;
        border-radius: 4px;
        color: #eef2ff;
        background-color: #573c77;
        display: grid;
        height: min-content;
        align-self: center;
    }


    .make-comments-container {
        display: flex;
        justify-content: center;
        column-gap: 20px;
        padding: 20px;
        width: 100%;
        max-width: 880px;
    }
    .make-comment-textarea {
        display: grid;
        align-self: start;
        width: 70%;
        height: 60px;
        resize: none;
        line-height: 2.5em; 
        text-align: left;
        background-color: #eef2ff;
        border: solid 1px #eef2ff;
        border-radius: 4px;
        padding-left: 15px;
        transition-timing-function: ease;
        transition-duration: 250ms;
    }

    .make-comment-textarea:hover {
        border-color: #6366f1;
    }

</style>