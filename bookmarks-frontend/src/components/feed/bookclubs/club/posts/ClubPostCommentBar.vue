<template>
  <div style="margin-top: 20px" :class="{ 'scrolled-below-post': comment }" ref="commentBarRef">
    <!-- If you have selected a comment to reply to then do that shit -->
    <span v-if="comment" class="text-sm ml-5 mb-2 block"
      >replying to
      <span class="text-indigo-500 fancy">{{ comment?.username }}'s'</span>
      comment
    </span>

    <div :class="{ 'comment-bar-section': comment }">
      <CommentBar
        :post-id="postId"
        :comment="comment"
        @pre-success-comment="(payload) => $emit('pre-success-comment', payload)"
      />

      <button
        v-if="comment"
        type="button"
        class="btn btn-tiny btn-red mb-2"
        @click="$emit('stop-commenting')"
      >
        <IconExit />
      </button>
    </div>
  </div>
</template>
<script setup>
// Vue
import {ref, onMounted} from 'vue';
// Services
import { helpersCtrl } from '@/services/helpers';
// Components
import CommentBar from './comments/CommentBar.vue';
import IconExit from '../../../../svg/icon-exit.vue';

const props = defineProps({
  comment: { type: Object, required: false },
  postId: { type: String, required: true },
  // Used to reply to parent comments in the case that you are 
  parentThread: { type: String, required: false}
});

defineEmits(['pre-success-comment', 'stop-commenting']);

const { debounce } = helpersCtrl;

// UI
const isScrollPastCommentBar = ref(false);
const commentBarRef = ref(null);
// This is all so we can have some smarter comment bar on desktop.
// probably bad component design on my part though.
onMounted(() => {
    const initialScrollHeight = window.scrollY;
    
    function handleScrollEvent() {
        console.log('called')
        
            console.log('made it apst first check')
            // im prefixing a dom element with $. 
            // All that means is that its the actual dom element 
            // Im adding an event listener to. CHat im just using slang.
            const $commentBar = commentBarRef.value;
            
            if ($commentBar) {
                const { bottom } = $commentBar.getBoundingClientRect();
                const isCurrentlyPastBottom = !!(bottom < 0);
                // if the value has changed since you last set it and the currnt scroll y is greater than the initial scroll y height.
                 // Only check if the user has scrolled past the initial scroll height

                if (initialScrollHeight + 20 <= window.scrollY) {
                    // Set to true only if it was previously false
                    if (!isScrollPastCommentBar.value && isCurrentlyPastBottom) {
                        isScrollPastCommentBar.value = true;
                        console.log('Scrolled past the comment bar');
                    }
                } else {
                    // If scrolling back up and the comment bar is visible, set to false
                    if (isScrollPastCommentBar.value && !isCurrentlyPastBottom) {
                        isScrollPastCommentBar.value = false;
                        console.log('Scrolled back up to the comment bar');
                        // if you haven't figured out what you want to say already, knock it off and make em reselect.
                        clubCommentSelectedForReply.value = null;
                    }
                }
            }
    }

    const debouncedScrollEvent = debounce(handleScrollEvent, 250, false);
    window.addEventListener('scroll', debouncedScrollEvent, {passive: true});
});
</script>
<style scoped>
@starting-style {
    .scrolled-below-post {
        opacity: 0;
    }
}

.scrolled-below-post {
    position: fixed;
    bottom: 20px;
    width: 90vw;
    max-width: 768px;
    z-index: 99999;
    background-color: var(--surface-primary);
    box-shadow: var(--shadow-lg);
    border-radius: var(--radius-md);
    padding: 20px;
    transition: all 250ms ease-in-out;
}
</style>