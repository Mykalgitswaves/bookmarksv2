<template>
    <div v-if="!props.comments.length && !props.pinnedComments.length">
        <p class="text-center text-2xl text-indigo-500 font-bold">Pretty quiet here... 🦗<span class="block text-lg font-medium text-slate-600">Get the conversation started with your opinion</span></p>
    </div>

    <div v-else>
        <TransitionGroup name="content" tag="ul"> 
            <li v-for="c in pinnedComments" :key="c.id" class="comments-wrapper">
                <Comment
                    :op-user-uuid="props.opUserUuid"
                    :comment="c.comment"
                    :is-liked="c.liked_by_current_user"
                    :replies="c.replies"
                    :num_replies="c.num_replies"
                    :likes="c.likes"
                    :is_pinned="!!c.pinned"
                    @comment-deleted="($event) => emit('comment-deleted', $event)"
                    @comment-unpinned="($event) => emit('comment-unpinned', $event)"
                />
            </li>
        </TransitionGroup> 

        <TransitionGroup name="content" tag="ul"> 
            <li v-for="c in props.comments" :key="c.id" class="comments-wrapper">
                <Comment
                    :op-user-uuid="props.opUserUuid"
                    :comment="c.comment"
                    :is-liked="c.liked_by_current_user"
                    :replies="c.replies"
                    :num_replies="c.num_replies"
                    :likes="c.likes"
                    :is_pinned="!!c.pinned"
                    @comment-deleted="($event) => emit('comment-deleted', $event)"
                    @comment-pinned="($event) => emit('comment-pinned', $event)"
                />
            </li>
        </TransitionGroup> 
    </div>
</template>
<script setup>
import Comment from './comment.vue';
import { ref } from 'vue';

const props = defineProps({
    comments: {
        type: Array,
        required: false,
    },
    pinnedComments: {
        type: Array,
        required: false,
    },
    postId: {
        type: String,
        required: true,
    },
    postUuid: {
        type: String,
        required: true,
    },
    opUserUuid: {
        type: String,
        required: true,
    }
});

const emit = defineEmits(['comment-deleted','comment-pinned']);



</script>