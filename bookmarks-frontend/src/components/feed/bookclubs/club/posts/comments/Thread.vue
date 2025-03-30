<template>
  <div
    class="thread"
    :class="{
      'replying-to': replyingToId === thread.id,
      'with-border-bottom': thread.depth === 1 && index !== 1,
      'subthread-comment-wrap': isSubThread,
      'deleted': thread.deleted
    }"
  >
    <div class="thread-columns">
      <span :class="{'selected': selectedComment}"></span>
      <!-- <div class="thread-spine-top"></div>  -->
      <!-- <ThreadTie /> -->
      <!-- <div class="thread-spine-bottom"></div>  -->
    </div>

    <div class="thread-body" 
      :class="{
        'selected': selectedComment,
        'navigatable': !threadDisabled && thread.num_replies > 0,
      }"
      @click.stop="() => threadDisabled ? undefined : navigateToThread()"
    >
      <!-- Helps us see things as replies -->

      <div class="thread-header">
        <h5 class="mr-2 text-stone-600 bold text-base">
          {{ thread?.username }}
        </h5>

        <p class="text-stone-500 text-xs">
          {{ dates.timeAgoFromNow(thread?.created_date, true) }}
        </p>
      </div>

      <div
        class="thread-copy"
      >
        <p class="text-sm text-stone-600 fancy">
          {{ thread?.text || 'sample comment' }}
        </p>
      </div>

      <div class="thread-footer">
        <button
          type="button"
          class="btn btn-tiny btn-icon text-stone-500 relative"
          @click.stop="replyToThread(thread)"
        >
          <IconClubComment />
            
          <span v-if="thread.num_replies > 0" class="fancy text-sm comment-count">{{ thread.num_replies }}</span>
        </button>

        <div class="flex gap-1">
          <button
            type="button"
            class="btn btn-tiny text-green-400 btn-specter ml-auto mr-2 relative"
            :class="{'bg-indigo-100': thread.liked_by_current_user}"
            @click.stop="thread.liked_by_current_user ? unlikeThread(thread) : likeThread(thread)"
          >
            <IconClubLike :class="{'one-80-deg': thread.liked_by_current_user}"/>

            <span class="fancy text-sm comment-count fancy">{{ thread.likes }}</span>
          </button>

          <!-- Controls for pinning and fun nerdage -->
          <div v-if="thread.depth === 0 && (thread.posted_by_current_user || post?.posted_by_current_user)" 
            class="absolute top-2 right-5"
          >
            <Popover>
              <PopoverTrigger as-child @click.stop>
                <Button @click.stop variant="ghost">
                  ...
                </Button>
              </PopoverTrigger>
              <PopoverContent class="w-fit">
                <div class="flex gap-2">
                  <Button
                    v-if="thread.posted_by_current_user" 
                    type="button"
                    variant="ghost"
                    class="btn btn-tiny btn-specter"
                    @click.stop="deleteThread(emit, thread)"
                    >
                    <IconTrash />
                  </Button>

                  <Button
                    v-if="post?.posted_by_current_user" 
                    type="button"
                    variant="ghost"
                    class="btn btn-tiny btn-specter"
                    @click.stop="pinThread(emit, index, thread)"
                  >
                    <IconPin />
                  </Button>
                  
              </div>
            </PopoverContent>
          </Popover>
        </div>

          
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
// vue
import { useRouter } from 'vue-router';
// services
import { Thread as threadProps, likeThread, unlikeThread, deleteThread, pinThread } from './threads';
import { dates } from '@/services/dates';
import { navRoutes } from '@/services/urls';
// Stores
import { useCurrentUserStore } from '@/stores/currentUser';
// Components
import IconClubLike from '../../awards/icons/ClubLike.vue';
import IconClubComment from '../../../../../svg/icon-club-comment.vue';
import IconTrash from '@/components/svg/icon-trash.vue';
import IconPin from '@/components/svg/icon-pin.vue';

import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/lib/registry/default/ui/popover';
import { Button } from '@/lib/registry/default/ui/button';

const props = defineProps({
  thread: {
    type: Object as () => threadProps,
    required: true,
  },
  replyingToId: {
    type: String,
    required: false,
  },
  index: {
    type: Number,
    required: true,
  },
  bookclubId: {
    type: String || null,
    default: null,
  },
  isSubThread: {
    type: Boolean,
    required: true,
    default: () => false,
  },
  // If this is a subthread we want to render information about who replied to who.
  parentToSubthread: {
    type: Object,
    required: false,
  },
  threadDisabled: {
    type: Boolean,
    default: false,
  },
  // If the view is 'main' we want to ignore what the depth is for subthread stuff. 
  // Ik this is convoluted but the easiest way to shine a turd.
  view: {
    type: String,
    required: false,
  },
  selectedComment: {
    type: Boolean,
    required: false,
    default: false,
  },
  post: {
    type: Object,
    required: false,
  },
});

const router = useRouter();

const store = useCurrentUserStore();
const { user } = store;

const emit = defineEmits([
  'thread-deleted',
  'thread-selected', 
  'comment-id-selected', 
  'navigating-threads', 
  'pre-success-thread-pinned', 
  'post-success-thread-prinned', 
  'error-pinning-thread',
]);

function replyToThread(thread: threadProps): void {
  const payload = { ...thread, index: props.index }
  emit('thread-selected', payload)
};

const toSubThreadRoute = props.bookclubId
  ? navRoutes.toSubThreadPage(
      user.id,
      props.bookclubId,
      props.thread?.post_id,
      props.thread.id
    )
  : '';

function navigateToThread() {
    if (props.isSubThread && props.view !== 'main') {
        console.log('is sub thread emit')
        emit('navigating-threads', props.thread.id)
    } else {
        console.log('to sub thread router push'); 
        router.push(toSubThreadRoute)
    }
};
</script>
<style scoped>
.thread {
  display: flex;
  flex-direction: row;
  align-items: center;
}

.thread.with-border-bottom {
  border-bottom: 1px var(--stone-200) solid;
}

.thread.replying-to {
  background-color: var(--indigo-100);
}

.thread .thread-columns {
  display: grid;
  grid-template-columns: repeat(var(--depth-num), 15px);
  align-self: start;
  position: relative;
}

.thread-columns.selected {
 padding-left: 15px;
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
  position: relative;
  padding: 6px 12px;
  width: 100%;
}

.absolute {
  position: absolute;
}

.thread-body.selected {
  border: 1px solid var(--stone-300);
  border-radius: 6px;
}

.thread-header {
  display: flex;
  align-items: center;
}

.thread-body.navigatable:hover {
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

.subthread-comment-wrap {
  margin-bottom: 10px;
  margin-left: 30px;
  margin-right: 15px;
  border-radius: 4px;
  border: 1px solid var(--stone-300);
  overflow: clip;
}

.comment-count {
  position: absolute;
  top: 0;
  right: -3px;
  line-height: 1;
  padding-top: 1px;
  padding-bottom: 1px;
  padding-left: 3px;
  padding-right: 3px;
  background-color: var(--stone-700);
  color: var(--stone-100);
  border-radius: 2px;
  font-size: var(--font-xs)
}

@starting-style {
  .deleted {
    opacity: 0;
  }
}

.deleted {
  opacity: 0;
  height: 0;
  visibility: hidden;
  transition: all 250ms ease-in-out; 
}
</style>
