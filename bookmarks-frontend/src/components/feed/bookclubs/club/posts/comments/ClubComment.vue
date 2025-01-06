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

<div v-else class="comment-nest-wrapper" :style="{ '--nest': 0 }">
    <!-- Real comment thread -->
     <!-- {{ Object.values(comment).find('post_id') }} -->
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
            <button 
                type="button"
            >
                
            </button>

            <button
                v-if="comment.num_replies > 0"
                type="button"
                class="btn btn-icon btn-tiny text-sm text-stone-700 underline"
                @click="showThread = !showThread"
            >
                View all {{ comment.num_replies }} comments
            </button>

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
</template>
<script setup>
import { computed } from 'vue';
import IconClubLike from '../../awards/icons/ClubLike.vue';
import { dates } from '../../../../../../services/dates';
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

const comment = computed(() => {
    return props.commentData.comment;
});

</script>
<style scoped>

@starting-style {
    .comment {
        opacity: 0;
        top: -9999;
    }
}

.comment {
    transition: all 250ms ease-in-out;
    margin-right: 12px;
    position: relative;
    padding: 4px 6px;
    background-color: var(--surface-primary);
    margin-left: 24px;  /* Space for the connector */
}

.comment-nest-wrapper {
    margin-left: calc(2ch * var(--nest, 0) );
    margin-top: 12px;
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


.comment::before {
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

/* Sibling comments or replies
.comments > * + *::after {
    content: '';
    position: absolute;
    top: -50%;
    left: -4px;
    width: 2px;
    height: calc(100% - 10px);
    background-color: var(--red-400)
} */

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
}
</style>