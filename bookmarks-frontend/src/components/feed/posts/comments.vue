<template>
    <div class="flex content-center px-2">
        <div class="make-comments-container main">
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
        <transition-group name="content" tag="ul">
            <li v-for="(comment, index) in comments" :key="index" class="comments-wrapper">
                <Comment
                    :comment="comment.comment"
                    :is-liked="comment.liked_by_current_user"
                    :replies="comment.replies"
                    :post-username="props.userUsername"
                    @comment-deleted="filterDeleteComments($event)"
                />
            </li>
        </transition-group>
    </div>
</template>
<script setup>
import { db } from '../../../services/db';
import { urls } from '../../../services/urls';
import { ref } from 'vue';
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
    },
    userUsername: {
        type: String,
        required: true,
    }
});

console.log(props.comments, 'props')

const comment = ref('');
const comments = ref(props.comments);
const replied_to = ref(null);

async function postComment(){
    const data = {
        "post_id": props.postId,
        "text": comment.value,
        "pinned": false,
        "replied_to": replied_to.value,
    };

    if(comment.value.length > 1){
        await db.post(urls.reviews.createComment(), data, true).then((res) => {
            comments.value.push({"comment": res.data, "replies": []})
        });
    };
};

function filterDeleteComments(comment_id) {
    comments.value = comments.value.filter((c) => {
        c.comment.id !== comment_id
    })
};

</script>