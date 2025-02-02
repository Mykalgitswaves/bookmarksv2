<template>
<div class="comment">
    <!-- Subgid for where the actual lines are coming from -->
    <div v-if="index !== 0" class="comment-thread-subgrid" :style="{'--max-subgrid-count': commentDepth}">
        <div class="collapse-comment-thread" :style="{'--column-start': commentDepth}">
            <button v-if="!subThreadCollapsed" type="button" class="btn btn-tiny">
                <IconMinus/>
            </button>

            <button v-if="subThreadCollapsed">
                <IconPlus/>
            </button>
        </div>
    </div>
    
    <!-- the actual comment -->
    <div class="comment-body">
        <div class="comment-header">
            <h5 class="mr-2 text-stone-600 bold text-base">{{ commentData.comment.username }}</h5>

            <p class="text-stone-500 text-xs">{{ dates.timeAgoFromNow(commentData.comment.created_date) }}</p>
        </div>

        <div class="comment-text">
            <p class="text-sm text-stone-600 fancy">
                {{ commentData.comment.text }}
            </p>
        </div>

        <div class="comment-footer">
            <button 
                type="button" 
                class="btn btn-tiny text-green-400 btn-specter mr-2"
                @click=""
                >
                <IconClubLike/>
            </button>
        </div>
    </div>
</div>
</template>
<script setup>
import IconPlus from '../../../../../svg/icon-plus.vue';
import IconMinus from '../../../../../svg/icon-chevron.vue'
import IconClubLike from '../../awards/icons/ClubLike.vue';
import { dates } from '../../../../../../services/dates';

defineProps({
    maxDepthOfThread: {
        type: Number,
        required: true,
        default: () => 3,
    },
    commentData: {
        type: Object,
        required: true,
    },
    commentDepth: {
        type: Number,
        required: true,
    },
    subThreadCollapsed: {
        type: Boolean
    },
    index: {
        type: Number,
    }
});
</script>
<style scoped>
.comment {
    display: flex;
    margin-left: 40px;
}

.comment-thread-subgrid {
    --subgrid-column-width: minmax(4vw, 30px);
    display: grid;
    /* 
        Max subgrid count is the total depth of the visible comments inside of a thread
        subgrid column width is the total width of each of the columns.
    */
    grid-template-columns: repeat(var(--max-subgrid-count), var(--subgrid-column-width));
}

.comment-thread-subgrid .collapse-comment-thread {
    position: relative;
    grid-column-start: var(--column-start);
    border-left: 1px solid var(--indigo-200);
    border-bottom: 1px solid var(--indigo-200);
    border-bottom-left-radius: 12px;
}
/* The expand thread button */
.comment-thread-subgrid .collapse-comment-thread button {
    position: absolute;
    left: -30%;
    top: -22%;
    transform: translateY(50%);
    padding: 4px;
    border-radius: 12px;
    background-color: var(--indigo-200)
}
</style>
<!--
    We are redoing comment threads. Instead of doing 
    them with absolutely positioned nonsense we are going to 
    be sophisticated nimrods and use a subgrid to compute the
    offset of each thread based on the depth of a reply.  
-->