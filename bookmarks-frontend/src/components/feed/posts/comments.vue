<template>
    <div v-if="!props.comments.length">
        <p class="text-center text-2xl text-indigo-500 font-bold">Pretty quiet here... 🦗<span class="block text-lg font-medium text-slate-600">Get the conversation started with your opinion</span></p>
    </div>

    <div v-else>
            <li v-for="c in cc" :key="c.id" class="comments-wrapper">
                <Comment
                    :comment="c.comment"
                    :is-liked="c.liked_by_current_user"
                    :replies="c.replies"
                    :post-username="props.userUsername"
                    @comment-deleted="filterDeleteComments"
                />
            </li>
    </div>
</template>
<script setup>
import { db } from '../../../services/db';
import { urls } from '../../../services/urls';
import { ref } from 'vue';
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

const cc = ref(props.comments);

function filterDeleteComments(comment_id) {
    console.log(cc.value, 'before filter')
    let temp = cc.value.find((c) => c.comment.id === comment_id)
    cc.value = cc.value.filter((c) => c.comment !== temp.comment);
    console.log(cc.value, 'after filter')
};

</script>