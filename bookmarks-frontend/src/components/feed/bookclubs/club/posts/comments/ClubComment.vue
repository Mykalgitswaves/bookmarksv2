<template>
<div v-if="isPreview" class="comment-nest-wrapper" :style="{ '--nest': 0 }">
    <div class="comment">
        <div class="comment-header">
            <h5 class="mr-2 text-stone-600 bold text-base">{{ comment.username }}</h5>

            <p class="text-stone-500 text-xs">{{ dates.timeAgoFromNow(comment.created_date) }}</p>
        </div>

        <div class="comment-body">
            <p class="text-sm text-stone-600 fancy">
                {{ comment.text }}
            </p>
        </div>

        <div class="comment-footer">
            <RouterLink 
                type="button"
                class="btn btn-icon btn-tiny text-sm text-stone-700 underline"
                :to="props.urlToCommentPage"
            >
                View all comments
            </RouterLink>

            <div>
                <button 
                    type="button" 
                    class="btn btn-tiny text-green-400 btn-specter mr-2"
                    >
                    <IconClubLike/>
                </button>
                
                <button 
                type="button"
                class="flipped btn btn-tiny text-red-400 btn-specter"
                >
                    <IconClubLike/>
                </button>
            </div>
        </div>
    </div>
</div>
<div v-else class="comments">
    <!-- Comments and replies -->
    <div class="comment-nest-wrapper" :style="{ '--nest': 0 }" ref="commentRef">
        <!-- Real comment thread -->
        <!-- {{ Object.values(comment).find('post_id') }} -->
        <div class="comment">
            <div class="comment-header">
                <h5 class="mr-2 text-stone-600 bold text-base">{{ comment?.username }}</h5>

                <p class="text-stone-500 text-xs">{{ dates.timeAgoFromNow(comment?.created_date, true) }}</p>
            </div>

            <div class="comment-body">
                <p class="text-sm text-stone-600 fancy">
                    {{ comment?.text }}
                </p>
            </div>

            <div class="comment-footer">
                <div class="flex gap-2 items-center w-100">
                    <button
                        v-if="comment?.num_replies > 1"
                        type="button"
                        class="btn btn-icon btn-tiny text-sm text-stone-700 underline"
                        @click="showThread = !showThread"
                    >
                        View all {{ comment?.num_replies }} comments
                    </button>

                    <button 
                        type="button"
                        class="btn btn-tiny btn-icon mr-auto"
                        :class="{'active': isShowingCommentBar}"
                        @click="isShowingCommentBar = !isShowingCommentBar"
                    >
                        <IconClubComment/>
                    </button>

                    <button 
                        type="button" 
                        class="btn btn-tiny text-green-400 btn-specter mr-2"
                        >
                        <IconClubLike/>
                    </button>
                    
                    <button 
                    type="button"
                    class="flipped btn btn-tiny text-red-400 btn-specter"
                    >
                        <IconClubLike/>
                    </button>
                </div>
            </div>
        </div>

        <CommentBar 
            v-if="isShowingCommentBar"  
            :post-id="comment.post_id"
            :comment="comment"
            @pre-success-comment="$emit('pre-success-comment', $event)" 
            @post-failure-comment="(err) => dispatchFailureToast(err)"
        />
    </div>

    <div v-for="reply in commentData.replies" :key="reply.id" class="comment-nest-wrapper" :style="{ '--nest': 1 }">
        <!-- Real comment thread -->
        <!-- {{ Object.values(comment).find('post_id') }} -->
        <div class="comment reply">
            <div class="comment-header">
                <h5 class="mr-2 text-stone-600 bold text-base">{{ reply.comment.username }}</h5>

                <p class="text-stone-500 text-xs">{{ dates.timeAgoFromNow(reply.comment.created_date, true) }}</p>
            </div>

            <div class="comment-body">
                <p class="text-sm text-stone-600 fancy">
                    {{ reply.comment.text }}
                </p>
            </div>

            <div class="comment-footer">

                    <button
                        v-if="comment?.num_replies > 1"
                        type="button"
                        class="btn btn-icon btn-tiny text-sm text-stone-700 underline"
                        @click="showThread = !showThread"
                    >
                        View all {{ comment?.num_replies }} comments
                    </button>

                    <button 
                        type="button"
                        class="btn btn-tiny btn-icon mr-auto"
                        :class="{'active': isShowingCommentBar}"
                        @click="isShowingCommentBar = !isShowingCommentBar"
                    >
                        <IconClubComment/>
                    </button>

                    <button 
                        type="button" 
                        class="btn btn-tiny text-green-400 btn-specter mr-2"
                        >
                        <IconClubLike/>
                    </button>
                    
                    <button 
                    type="button"
                    class="flipped btn btn-tiny text-red-400 btn-specter"
                    >
                        <IconClubLike/>
                    </button>
            </div>
        </div>

        <CommentBar 
            v-if="isShowingCommentBar"  
            :post-id="comment.post_id"
            :comment="comment"
            @pre-success-comment="$emit('pre-success-comment', $event)" 
            @post-failure-comment="(err) => dispatchFailureToast(err)"
        />

        <dialog class="deleteDialog">

        </dialog>
    </div>
</div>
</template>
<script setup>
import { computed, ref, onMounted } from 'vue';
import IconClubLike from '../../awards/icons/ClubLike.vue';
import { dates } from '../../../../../../services/dates';
import IconClubComment from '../../../../../svg/icon-club-comment.vue';
import CommentBar from './CommentBar.vue';
import SuccessToast from '../../../../../shared/SuccessToast.vue';
import TouchEvent from '../../../../../../services/swipe';
import { deleteComment, likeComment } from './comment';

const props = defineProps({
    isPreview: {
        type: Boolean,
        required: true,
    },
    urlToCommentPage: {
        type: String,
        required: false,
    },
    commentData: {
        type: Object,
        required: true,
    }
});

const emit = defineEmits(['pre-success-comment']);

const comment = computed(() => {
    return props.commentData.comment;
});

const isShowingCommentBar = ref(false);
const commentRef = ref(null);

onMounted(() => {
    let commentElement = commentRef.value.el
    let touchEvent = null;

    commentElement.addEventListener('touchstart', (event) => {
        touchEvent = new TouchEvent(event);
    });

    commentElement.addEventListener('touchend', handleSwipe);

    function handleSwipe(event) {
        if (!touchEvent) {
            return;
        }

        touchEvent.setEndEvent(event);

        if (touchEvent.isSwipeLeft()) {
            // delete comment
            deleteComment(props.commentData.comment);
        }

        // Reset event for next touch
        touchEvent = null;
    }
})

</script>
<style scoped>

@starting-style {
    .comment {
        opacity: 0;
        left: -10000px;
        height: 0;
    }
}

.comment {
    transition: all 250ms ease-in-out;
    margin-right: 12px;
    position: relative;
    padding: 4px 6px;
    background-color: var(--surface-primary);
    margin-left: 24px;  /* Space for the connector */
    transition: all 250ms ease-in-out; 
    left: 0;
}

.comment-nest-wrapper {
    margin-left: calc(2ch * var(--nest, 0) );
    position: relative;
}

/* .comment::before {
    content: '';
    position: absolute;
    background-color: var(--indigo-400);
    width: 6px;
    height: 6px;
    top: 15px;
    left: -6px;
} */


.comment.reply::before {
    content: '';
    position: absolute;
    left: -16px;  /* Adjust based on your indentation needs */
    top: 0;
    width: 16px;  /* Width of the curve */
    height: 20px; /* Height of the curve - adjust based on your needs */
    border-left: 2px solid var(--indigo-300);  /* Discord-like gray color */
    border-bottom: 2px solid var(--indigo-300);
    border-bottom-left-radius: 8px;  /* Creates the curve */
}

.comment:not(:last-child)::after {
    content: '';
    position: absolute;
    left: -16px;
    bottom: 20px;  /* Should match the height in ::before */
    bottom: 0;
    width: 2px;
    background: var(--indigo-300);  /* Same color as the curve */
}

.comment:hover {
   
}

.comment-header {
    display: flex;
    align-items: center;
}

.comment-body {
    margin-top: 4px;
    padding-top: 4px;
    padding-bottom: 4px;
    padding-left: 8px;
    background-color: var(--stone-100);
    border-radius: 4px;
}

.comment-footer {
    display: flex;
    justify-content: space-between;
    align-items: start;
    width: 100%;
}
</style>