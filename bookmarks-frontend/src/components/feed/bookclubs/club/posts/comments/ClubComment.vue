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

            <button 
                type="button" 
                class="btn btn-tiny text-green-400 btn-specter mr-2"
                @click="likeClubComment(comment)"
                >
                <IconClubLike/>
            </button>
        </div>
    </div>
</div>
<div v-else class="comments">
    <!-- Comments and replies -->
    <div class="comment-nest-wrapper" :style="{ '--nest': 0 }" ref="commentRef">
        <!-- Real comment thread -->
        <!-- {{ Object.values(comment).find('post_id') }} -->
        <div v-if="!isDeletingView" 
            class="comment"
            :class="{'replying-to': props.isReplyingToKey ? props.isReplyingToKey === comment?.id : false}"
        >
            <div class="comment-header">
                <h5 class="mr-2 text-stone-600 bold text-base">
                    {{ comment?.username || 'test'}}
                </h5>

                <p class="text-stone-500 text-xs">
                    {{ dates.timeAgoFromNow(comment?.created_date, true) }}
                </p>
            </div>

            <div class="comment-body">
                <p class="text-sm text-stone-600 fancy">
                    {{ comment?.text || 'sample comment' }}
                </p>
            </div>

            <div class="comment-footer">
                <div class="flex gap-2 items-center w-100">
                    <!-- THis is mobile, only show up on mobile -->
                    <button 
                        role="mobile-comment"
                        type="button"
                        class="btn btn-tiny btn-icon mobile-only"
                        :class="{'active': isShowingCommentBar}"
                        @click="
                            selectCommentAndShowCommentBarFooter(comment); 
                            isShowingCommentBar = true;
                        "
                    >
                        <IconClubComment/>
                    </button>
                    <!-- This is desktop one. -->
                    <button 
                        role="mobile-comment"
                        type="button"
                        class="btn btn-tiny btn-icon desktop-only"
                        :class="{'active': isShowingCommentBar}"
                        @click="
                            emit('comment-selected', {comment, index}) 
                        "
                    >
                        <IconClubComment/>
                    </button>

                    <button 
                        type="button" 
                        class="btn btn-tiny text-green-400 btn-specter mr-2 ml-auto"
                        @click=""
                        >
                        <IconClubLike/>
                    </button>

                    <button 
                        type="button" 
                        class="btn btn-tiny text-green-400 btn-specter ml-2"
                        @click="isDeletingView = true"
                        >
                        <IconTrash/>
                    </button>
                </div>
            </div>
        </div>

        <!-- Are you deleting a comment, make people confirm that they want to do this! -->
        <div v-if="isDeletingView" class="comment deleting">
            <button 
                class="btn btn-large btn-red fancy" 
                @click="deleteClubComment(props.commentData.comment);"
            >
                delete
            </button>

            <button class="btn btn-large btn-green fancy" @click="isDeletingView = false">
                cancel
            </button>
        </div>
    </div>

    <div v-for="reply in commentData.replies" 
        :key="reply?.id" 
        class="comment-nest-wrapper" 
        :ref="(reply) => replyDistanceMapping[reply?.id] = reply"
        :style="{ '--nest': 1, '--distance-from-top': generateDistanceFromTopComment(reply?.id) }"
    >
        <!-- Real comment thread -->
        <!-- {{ Object.values(comment).find('post_id') }} -->
        <div class="comment reply" :class="{'replying-to': reply.comment?.id ? props.isReplyingToKey === reply.comment?.id : false}">
            <div class="comment-header">
                <h5 class="mr-2 text-stone-600 bold text-base">{{ reply.comment?.username || 'test replier' }}</h5>

                <p class="text-stone-500 text-xs">{{ dates.timeAgoFromNow(reply.comment?.created_date, true) }}</p>
            </div>

            <div class="comment-body">
                <p class="text-sm text-stone-600 fancy">
                    {{ reply.comment?.text || 'sample reply' }}
                </p>
            </div>

            <div class="comment-footer">
                <!-- Mobile only -->
                <button 
                    type="button"
                    class="btn btn-tiny btn-icon mobile-only"
                    :class="{'active': isShowingCommentBar}"
                    @click="selectCommentAndShowCommentBarFooter(reply.comment, reply.comment.id)"
                >
                    <IconClubComment/>
                </button>

                <!-- Desktop -->
                <button 
                    type="button"
                    class="btn btn-tiny btn-icon desktop-only"
                    :class="{'active': isShowingCommentBar}"
                    @click="replyToReply(reply.comment, reply.comment.id)"
                >
                    <IconClubComment/>
                </button>


                <button 
                    type="button" 
                    class="btn btn-tiny text-green-400 btn-specter ml-auto mr-2"
                    @click="likeClubComment(reply.comment)"
                    >
                    <IconClubLike/>
                </button>
            </div>
        </div>
    </div>

    <!-- If you have more than two replies to preview you need to make your users click into get the next ten -->
    <!-- hasExpandedComments gets reset to false on every call to pagination endpoint -->
    <div v-if="commentData.comment?.num_replies > 2 && !hasExpandedComments" 
        class="comment-nest-wrapper" 
        :style="{
            '--nest': 1,
            '--distance-from-top': generateDistanceFromTopComment(undefined)
        }"
    >
        <div class="more-comments">
            <button type="button" class="flex items-center gap-2">
                <IconPlus /> 
                
                <span>{{ commentData.comment.num_replies - 2 }} more comments</span>
            </button>
        </div>
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
import { deleteClubComment, likeClubComment, dislikeClubComment } from './comment';
import { PubSub } from '../../../../../../services/pubsub'; 
import IconTrash from '../../../../../svg/icon-trash.vue';
import IconPlus from '../../../../../svg/icon-plus.vue';

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
    },
    // light up the ui
    isReplyingToKey: {
        type: String,
        required: false,
    },
    // Used to find where to insert replies to if the user is replying.
    index: {
        type: Number,
        required: true
    }
});

const emit = defineEmits(['pre-success-comment', 'comment-selected']);

const comment = computed(() => {
    return props.commentData.comment;
});

const isShowingCommentBar = ref(false);
const commentRef = ref(null);
const isDeletingView = ref(false);

/**
 * @distance function for setting the height of --distance-from-top, which allows us 
 * to know exactly how far away the distances are on the y axis for calculating each
 * ::after height for the comments. This gives us the ability to create a comment thread 
 * appearance to our commments feature similar to what reddit uses.  
 * @dependency { replyDistanceMapping } - a dictionary containing the id's of each reply $element and their corresponding dom ref needed to do calculations.
 * @dependency commentRef - a global ref constant that can be used to find the parent comment in the dom.
 * @function generateDistanceFromTopComment -  A function that accepts an id, and returns an integer (in pixels) for the height
 *  difference between the yOffset of the provided reply and the original comment. 
 * @returns String in pixels of the height used for each comment
 */
const replyDistanceMapping = ref({});
// I know these are global but save us from having to recompute every time this runs.
let $parentComment;
let parentBoundingRect;

function generateDistanceFromTopComment(replyId) {
    // If this function receives a falsey value it means that you are calculating 
    // the distance between a view more comments button and the first reply (otherwise known as the offset).
    // so calling object keys should not be that expensive. 
    // At most it iterates through every comment in the viewport one time. 
    if (replyId === undefined && Object.keys(replyDistanceMapping.value).length) {
        const $firstReply = Object.values(replyDistanceMapping.value)[0];
        const { top, bottom } = $firstReply.getBoundingClientRect();

        return `${Math.abs(bottom) - Math.abs(top)}px`
    }

    if (!$parentComment && commentRef.value) {
        $parentComment = commentRef.value;
        parentBoundingRect = $parentComment.getBoundingClientRect();
    }
    // instantiate a temp var, $means non v dom element. 
    const $reply = replyDistanceMapping.value[replyId];

    // Early out if you dont have a reply.
    if (!$reply) return;

    // Find the bottom of the parent comment
    const replyBoundingRect = $reply.getBoundingClientRect();

    return `${(replyBoundingRect.top + window.scrollY) - (parentBoundingRect.bottom + window.scrollY)}px`; 
}


onMounted(() => {
    let commentElement = commentRef.value
    let touchEvent = null;

    commentElement.addEventListener(
        'touchstart', 
        (event) => {
            touchEvent = new TouchEvent(event);
        }, 
        { passive: true }
    );

    commentElement.addEventListener(
        'touchend', 
        handleSwipe, 
        { passive: true }
    );

    function handleSwipe(event) {
        if (!touchEvent) {
            return;
        }

        touchEvent.setEndEvent(event);

        if (touchEvent.isSwipeLeft()) {
            // delete comment
            isDeletingView.value = true;
        }

        // Reset if they swipe right after opening delete view.
        if (isDeletingView.value && touchEvent.isSwipeRight()) {
            isDeletingView.value = false;
        }

        // Reset event for next touch
        touchEvent = null;
    }
})

/**
 * @description - function that selects the clicked comment 
 * and reveals a comment bar in the footer.
 * @param comment - Proxy object.
 * @returns { void }
 */
function selectCommentAndShowCommentBarFooter(comment, replyingToId) {
    // If you are replying to a someones reply put which one. 
    if (replyingToId) {
        comment.replyingTo = replyingToId;
    }

    PubSub.publish('start-commenting-club-post', 
        {
            comment: comment, 
            index: props.index, 
        }
    );
}

function replyToReply(comment, repliedToId) {
    comment.replyingTo = repliedToId;
    emit('comment-selected', comment)
}
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
    --comment-inline-start-margin: 8px;
    --comment-inline-end-margin: 0;
    
    @media screen and (max-width: 768px)  {
        --comment-inline-end-margin: 8px;
    }

    transition: all 250ms ease-in-out;
    margin-right: var(--comment-inline-end-margin);
    position: relative;
    padding: 4px 6px;
    background-color: var(--surface-primary);
    margin-left: var(--comment-inline-start-margin);  /* Space for the connector */
    transition: all 250ms ease-in-out; 
    left: 0;
}

.comment.deleting {
    left: 0;
    right: 0;
    background-color: var(--stone-50);
    border: 1px solid var(--stone-300);
    display: grid;
    grid-template-columns: 1fr 1fr;
    column-gap: 12px;
    padding: 8px;
    margin-top: 8px; 
    margin-bottom: 8px; 
}


.comment-nest-wrapper {
    margin-left: calc(5% * var(--nest, 0));
    position: relative;
    scroll-behavior: smooth;
    overflow-x: auto;
    overflow-x: visible;
}

.comment.reply { margin-bottom: unset; }

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
    bottom: var(--distance-from-top);  /* Should match the height in ::before */
    bottom: 0;
    width: 2px;
    background: var(--indigo-300);  /* Same color as the curve */
}

.more-comments {
    position: relative;
    font-size: var(--font-sm);
    margin-left: 8px;
    font-family: var(--fancy-script);
    text-decoration: underline;
    padding-left: 4px;
}

.more-comments::before {
    content: '';
    position: absolute;
    left: calc(var(--nest) * -16px);  /* Adjust based on your indentation needs */
    bottom: 10px;
    width: calc(var(--nest) * 16px);  /* Width of the curve */
    height: calc(var(--distance-from-top) - 20px); /* Height of the curve - adjust based on your needs */
    border-left: 2px solid var(--indigo-300);  /* Discord-like gray color */
    border-bottom: 2px solid var(--indigo-300);
    border-bottom-left-radius: 8px;  /* Creates the curve */
}

.more-comments::after {
    content: '';
    position: absolute;
    left: -16px;
    bottom: var(--distance-from-top);  /* Should match the height in ::before */
    bottom: 0;
    width: 2px;
    background: var(--indigo-300);
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

.comment.replying-to {
    border: 2px dotted var(--indigo-500);
    background-color: var(--surface-primary);
    box-shadow: var(--shadow-lg);
    border-radius: var(--radius-sm);
    padding: 8px;
}
</style>