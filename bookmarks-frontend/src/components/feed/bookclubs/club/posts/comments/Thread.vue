<script setup lang="ts">
import { useRouter } from 'vue-router';
import { Thread as threadProps } from './threads';
import { dates } from '@/services/dates';
import { navRoutes } from '@/services/urls';
import { currentUser } from '@/stores/currentUser';
import IconClubLike from '../../awards/icons/ClubLike.vue';
import IconClubComment from '../../../../../svg/icon-club-comment.vue';
import ThreadTie from './ThreadTie.vue';

const props = defineProps({
    thread: {
        type: Object as () => threadProps,
        required: false,
    },
    replyingToId: {
        type: String,
        required: false,
    },
    index: {
        type: Number,
        required: false,
    },
    bookclubId: {
        type: String || null, 
        default: null,
    }
});

const router = useRouter(); 
const emit = defineEmits(['thread-selected', 'comment-id-selected'])
// used to assign a darker color based on the depth of reply

function replyToThread(thread: threadProps):void {
    const payload = { ...thread, index: props.index };
    emit('thread-selected', payload);
}

const toSubThreadRoute = props.bookclubId ? navRoutes.toSubThreadPage(currentUser.value.id, props.bookclubId, props.thread.post_id, props.thread.id) : '';

console.log(toSubThreadRoute)
</script>
<template>
    <div class="thread"
        :class="{'replying-to': replyingToId === thread.id,
            'with-border-bottom': thread.depth === 1 && index !== 1
        }"
        @click="router.push(toSubThreadRoute)"
    >
        <div class="thread-columns">
            <!-- <div class="thread-spine-top"></div>  -->
            <ThreadTie />
            <!-- <div class="thread-spine-bottom"></div>  -->
        </div>

        <div class="thread-body">
            <div class="thread-header">
                <h5 class="mr-2 text-stone-600 bold text-base">
                    {{ thread?.username}}
                </h5>

                <p class="text-stone-500 text-xs">
                    {{ dates.timeAgoFromNow(thread?.created_date, true) }}
                </p>
            </div>
            
            <div class="thread-copy">
                <p class="text-sm text-stone-600 fancy">
                    {{ thread?.text || 'sample comment' }}
                </p>
            </div>

            <div class="thread-footer">
                <button 
                    type="button"
                    class="btn btn-tiny btn-icon desktop-only"
                    @click="replyToThread(thread)"
                >
                    <IconClubComment/>

                    <span v-if="thread.num_replies > 0" class="fancy text-sm">{{ thread.num_replies }}</span>
                </button>


                <button 
                    type="button" 
                    class="btn btn-tiny text-green-400 btn-specter ml-auto mr-2"
                    @click="likeThread(thread)"
                    >
                    <IconClubLike/>
                </button>
            </div>
        </div>
    </div>
</template>
<style scoped>
    .thread {
        display: flex;
        flex-direction: row;
        align-items: center;
        margin-top: 4px;
        margin-bottom: 4px;
    }

    .thread.with-border-bottom {
        border-bottom: 1px var(--stone-200) solid;
    }

    .thread.replying-to {
        background-color: var(--indigo-300);
    }

    .thread .thread-columns {
        display: grid;
        grid-template-columns: repeat(var(--depth-num), 15px);
        align-self: start;
        position: relative;
    }

    .thread-columns svg {
        margin-top: 10px;
    }

    .thread-spine-bottom {
        position: absolute;
        background-color: var(--indigo-200);
        width: 2px;
        top: -20%;
        bottom: 60%;
        left: 49%;
    }

    .thread-line {
        align-self: end;
        height: calc(var(--comment-height) * 1px);
        width: 2px;
        background-color: var(--indigo-300);
    }

    .thread .thread-body {
        padding: 4px 8px;
        width: 100%;
    }

    .thread-header {
        display: flex;
        align-items: center;
    }

    .thread:hover .thread-copy {
        background-color: var(--indigo-100);
        cursor: pointer;
    }

    .thread-copy {
        margin-top: 4px;
        padding-top: 4px;
        padding-bottom: 4px;
        padding-left: 8px;
        border-radius: 4px;
        transition: all 250ms ease-in-out;
    }

    .thread-footer {
        display: flex;
        justify-content: space-between;
        align-items: start;
        width: 100%;
    }
</style>