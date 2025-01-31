<template>
    <form class="flex gap-2 items-center" @submit.prevent="debouncedPostComment(modelComment)">
        <div class="searchbar" :class="{'comment': !!props.comment}">
            <!-- <div class="searchbar-prefix">
               🙋
            </div> -->

            <textarea 
                class="comment-textarea" 
                type="text" 
                :max="XLARGE_TEXT_LENGTH" 
                v-model="modelComment" 
            />

            <div class="searchbar-end">
                <button 
                    type="submit" 
                    :disabled="submitting"
                    class="btn btn-tiny btn-submit fancy submit-comments" 
                >
                    submit
                </button>
            </div>
        </div>
    </form>

    <Teleport to="body">
        <SuccessToast v-if="toast" :toast="toast" :toast-type="Toast.TYPES.MESSAGE_TYPE" @dismiss="() => toast = null"/>
    </Teleport>
</template>
<script setup>
import { ref } from 'vue';
import { urls } from '../../../../../../services/urls';
import { db } from '../../../../../../services/db';
import { XLARGE_TEXT_LENGTH } from '../../../../../../services/forms';
import { helpersCtrl } from '../../../../../../services/helpers';
import SuccessToast from '../../../../../shared/SuccessToast.vue';
import { Toast } from '../../../../../shared/models';

const props = defineProps({
    postId: {
        type: String,
        required: true,
    },
    // used to reply to a comment
    comment: {
        type: Object,
        required: false,
    }
});

const submitting = ref(false);
const modelComment = ref('')
const emit = defineEmits(['comment-created', 'pre-success-comment']);
const { debounce } = helpersCtrl;
const toast = ref(null);


// Used to post comments.
async function postComment() {
    submitting.value = true;
    let data;
    // If you are commenting on a post, not replying 
    if (!props.comment) {
        data = {
            post_id: props.postId,
            text: modelComment.value,
            pinned: false,
            replied_to: null,
        }
    } else {
        data = {
            post_id: props.postId,
            text: modelComment.value,
            pinned: false,
            replied_to: props.comment.replyingTo || props.comment.id // see if you are replying to a reply, if not see if you are replying to a comment
        }
    }

    // Used for snappier feeling comments, in case you want dont want to wait for the post.
    emit('pre-success-comment', modelComment.value);

    db.post(urls.reviews.createComment(), 
        data, 
        false, 
        (res) => {
            emit('comment-created', res.data);
            modelComment.value = '';
            toast.value = {
                message: 'Comment created 🎉',
            }
            submitting.value = false;
        }, 
        () => {
            emit('post-failure-comment');
            submitting.value = false;
        }
    );
};

const debouncedPostComment = debounce(postComment, 500, true);
</script>
<style scoped>

.searchbar {
    display: flex;
    align-items: center;
    border: 1px solid var(--indigo-300);
    border-radius: var(--radius-sm);
    width: 97%;
    margin-left: auto;
    margin-right: auto;
    padding-left: 8px;
    padding-right: 8px;
    position: relative;
    background-color: var(--surface-primary);
}

.searchbar.comment {
    width: 90%;
    margin-bottom: 10px;
}

.searchbar-prefix {
    padding-right: 4px;
    font-family: var(--fancy-script);
    color: var(--stone-400);
    background-color: var(--surface-primary);
}

textarea {
    --min-height: 5ch;
    appearance: none;
    border: none;
    color: var(--stone-600);
    font-size: var(--text-sm);
    width: 95%;
    min-height: var(--min-height);
    resize: none;
    transition: all 250ms ease-in-out;
    word-break: break-all;
}

textarea:focus {
    --min-height: 10ch;
    outline: none;
    padding-top: 6px;
    padding-bottom: 6px;
    min-height: var(--min-height);
}

textarea::placeholder {
    position: absolute;
    top: 55%;
    transform: translateY(55%);
    padding-left: 20px;
    font-size: var(--font-sm)
}

.submit-comments {
    --font-size: var(--font-sm);

    /* Decrease for mobile so you have more horizontal clearance */
    @media screen and (max-width: 768px) {
        --font-size: var(--font-xs);
    }

    height: 40px;
    font-size: var(--font-size);
}
</style>