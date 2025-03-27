<template>
  <div class="subthread">
    <BackBtn :back-fn="() => $router.push(navRoutes.toBookClubFeed(currentUser.id, bookclub))"/>
      
    <!-- Post -->
    <KeepAlive>
      <AsyncComponent :promises="[loadPostPromise]">
        <template #resolved>
          <div class="subthread-wrap">
            <ClubPost v-if="postData" :post="postData" />
          </div>

          <ViewAwards />
        </template>
        <template #loading></template>
      </AsyncComponent>
    </KeepAlive>

    <!-- Sub Thread -->
    <AsyncComponent :promise-factory="getCommentsFactory" :subscribed-to="GET_COMMENTS_KEY">
      <template #resolved>
        <div class="pb-1 pt-1 border-b-light">
          <!-- New parent of parent thread -->
          <BackBtn :back-fn="() => goUpThread()" margin-left="md:ml-5">
            <template #button-text>
              <span class="fancy text-sm">
                Back to post
              </span>
            </template>
          </BackBtn>
        </div>


        <div v-if="ancestorThreads.length" class="ancestor-threads">
          <ThreadComponent
            v-for="thread in ancestorThreads"
            :thread="thread"
            :thread-disabled="true"
            :is-sub-thread="false"
            @thread-selected="(thread) => clubCommentSelectedForReply = thread"
          />
        </div>

        <div class="parent-thread-seperator"></div>

        <!-- current comment-->
         <div class="current-comment">
          <ThreadComponent
            :thread="parentThread"
            :thread-disabled="true"
            :is-sub-thread="false"
            :parent-to-subthread="
              ancestorThreads.find((thread) => thread.id === parentThread?.replied_to) || null
            "
            :selected-comment="true"
            @thread-selected="
              (thread) => {
                clubCommentSelectedForReply = thread
              }
            "
          />
        </div>

        <ClubPostCommentBar
          v-if="clubCommentSelectedForReply"
          :post-id="postData.id"
          :comment="clubCommentSelectedForReply"
          @stop-commenting="clubCommentSelectedForReply = null"
        />

        <div class="thread-seperator mb-2 mt-2">
          <button v-if="commentData.length"
            class="ml-7 text-stone-500 text-sm fancy flex items-center gap-2"
            type="button"
            @click="showingReplies = !showingReplies"
          >
            <span v-if="!showingReplies">Hiding</span>

            <span v-if="showingReplies">Viewing</span>

            {{ commentData.length }} Replies

            <IconChevron />
          </button>

          <h5 v-else class="ml-5 text-stone-500 text-sm fancy">No replies</h5>
        </div>

        <div v-if="commentData.length && showingReplies" class="subthread-comment-wrap">
          <ThreadComponent
            v-for="(thread, index) in commentData"
            :key="thread.id"
            :index="index"
            :bookclub-id="bookclub"
            :thread="thread"
            :is-sub-thread="true"
            :parent-to-subthread="parentThread"
            :replying-to-id="clubCommentSelectedForReply?.id || threadId"
            @thread-selected="(thread) => (clubCommentSelectedForReply = thread)"
            @navigating-threads="(threadId) => descendThread(threadId)"
            @deleted-thread="(threadId) => removeThreadFromReplies(threadId)"
          />
        </div>
      </template>

      <template #loading>
        <div class="loading gradient p-5 text-center fancy">Loading comments</div>
      </template>
    </AsyncComponent>
  </div>
</template>
<script setup lang="ts">
// Vue
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
// Services
import { db } from '@/services/db'
import { urls, navRoutes } from '@/services/urls'
import { PubSub } from '@/services/pubsub'
import { PostResponse } from '@/components/feed/bookclubs/club/posts/comments/threads'
// Stores
import { currentUser } from '@/stores/currentUser'
// Types
import { Thread } from '../comments/threads'
// Components
import BackBtn from '@/components/feed/partials/back-btn.vue'
import AsyncComponent from '@/components/feed/partials/AsyncComponent.vue'
import ClubPost from '../ClubPost.vue'
import ClubPostCommentBar from '../ClubPostCommentBar.vue'
import ThreadComponent from './Thread.vue'
import ViewAwards from '../../awards/ViewAwards.vue'
import IconChevron from '@/components/svg/icon-chevron.vue'

// Params
const route = useRoute()
const router = useRouter()
const { bookclub, postId, threadId } = route.params

// Data refs
const commentData = ref<Array<Thread> | []>([])
const postData = ref({})
const parentThread = ref<Thread | null>(null)
// Whats before a parent thread, an ancestor thread is all the context from above a subthread.
const ancestorThreads = ref<Thread[]>([])
const showingReplies = ref(true)

/**
 * @load_comments
 */
const GET_COMMENTS_KEY = 'sub-thread-get-comments'
// for comment bar.
const clubCommentSelectedForReply = ref<Thread | null>(null)

// Needed for descending navigationThread gets updated in descendThread.
const navigationThread = ref<String | null>(null)

const computedUrl = computed(() => {
  if (navigationThread.value) {
    return urls.reviews.getCommentForComments(postId, navigationThread.value)
  } else {
    return urls.reviews.getCommentForComments(postId, threadId)
  }
});

async function getCommentsFactory() {
  const ancestorThreadPromiseFactory = () =>
    db.get(
      urls.concatQueryParams(`${computedUrl.value}/parent_comments`, { book_club_id: bookclub }),
      null,
      false,
      (res: any) => {
        ancestorThreads.value = res.data.comments
      },
      (err: any) => {
        console.warn(err)
      }
    )

  const threadPromiseFactory = () =>
    db.get(
      urls.concatQueryParams(computedUrl.value, {
        book_club_id: bookclub,
      }),
      null,
      false,
      (res: any) => {
        commentData.value = res.data.comments
        parentThread.value = res.data.parent_comment
      },
      (err: any) => console.warn(err)
    )

  return Promise.allSettled([ancestorThreadPromiseFactory(), threadPromiseFactory()]);
}

// Remove the thread from the ui.
function removeThreadFromReplies(threadId: string) {
  commentData.value = commentData.value.filter((thread) => thread.id !== threadId);
};

const loadPostPromise = db.get(
  urls.concatQueryParams(urls.bookclubs.getClubFeed(bookclub), { post_id: postId }),
  null,
  false,
  (res: PostResponse) => {
    console.log(res, 'loading the post data bruh')
    postData.value = res.posts
  },
  (err: Error) => {
    console.error(err)
  }
)
// #TODO: Fill out this other case (non club) next.
/** @endLoad */

/**
 * @nav_function
 * We need a way to intelligently navigate up to the past depth you were on.
 * If the parentComment is a reply, then we need to refresh the subscription key to load all new comments,
 * otherwise if its null we know we are on level 0 depth.
 */
function goUpThread() {
  if (parentThread.value?.replied_to) {
    PubSub.publish(GET_COMMENTS_KEY)
  } else {
    // If bookclub url is different,
    router.push(navRoutes.toBookClubCommentPage(currentUser.value?.id, bookclub, postId))
  }
}

function descendThread(threadId: string) {
  navigationThread.value = threadId
  PubSub.publish(GET_COMMENTS_KEY)
}
</script>
<style scoped>
.ancestor-threads {
  border-bottom: 1px solid var(--stone-300);
}

.ancestor-threads .thread-body {
  padding-left: 12px;
  padding-right: 12px;
}

.current-comment {
  padding-left: 14px;
  padding-right: 14px;
}

.current-comment ::v-deep.thread .thread-body {
  border: 1px solid var(--stone-300) !important;
  border-radius: 6px;
}

.subthread {
  border: 1px solid var(--stone-300);
}

.subthread-wrap {
  padding: 20px 2rem;
  border: 1px solid var(--stone-300);
  border-left-width: 0;
  border-right-width: 0;
}

.subthread-comment-wrap .thread-body {
  padding-left: 12px;
  padding-right: 12px;
}

.thread-seperator {
  width: 100%;
  padding-top: 10px;
  padding-bottom: 10px;
}

.parent-thread-seperator {
  width: 100%;
  padding-bottom: 10px;
  padding-left: 20px;
  min-height: 30px; 
  border-left: 1px solid var(--stone-300);
  margin-left: 5%;
}
</style>
