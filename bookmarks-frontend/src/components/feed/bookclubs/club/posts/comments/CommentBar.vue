<template>
    <form class="flex gap-2 items-center" @submit.prevent="postComment(modelComment)">
        <div class="searchbar">
            <div class="searchbar-prefix">
                $
            </div>
            <textarea 
                class="comment-textarea" 
                type="text" 
                :max="XLARGE_TEXT_LENGTH" 
                v-model="modelComment" 
                placeholder="Got something on your mind?" 
            />

            <div class="searchbar-end">
                <button class="btn btn-tiny btn-submit fancy submit-comments" type="submit">
                    submit
                </button>
            </div>
        </div>

    </form>
</template>
<script setup>
import { ref } from 'vue';
import { urls } from '../../../../../../services/urls';
import { db } from '../../../../../../services/db';
import { XLARGE_TEXT_LENGTH } from '../../../../../../services/forms';

const props = defineProps({
    postId: {
        type: String,
        required: true,
    }
});

const modelComment = ref('')
const emit = defineEmits(['comment-created']);

async function postComment() {
    const data = {
        post_id: props.postId,
        text: modelComment.value,
        pinned: false,
        replied_to: null,
    }

    db.post(urls.reviews.createComment(), data, false, (res) => {
        emit('comment-created', res.data);
    }, (err) => {
        console.error(err);
    });
}
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
}

.searchbar-prefix {
    padding-right: 4px;
    font-family: var(--fancy-script);
    color: var(--stone-400);
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
    top: 50%;
    transform: translateY(-50%);
    left: 10px;
}

.submit-comments {
    height: 40px;
    font-size: var(--font-sm);
}
</style>