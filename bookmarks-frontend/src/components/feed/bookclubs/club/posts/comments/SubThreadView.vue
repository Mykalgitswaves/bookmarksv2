<template>
  <div class="subthread">
    <BackBtn :back-fn="() => goUpThread()" />
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
        <!-- New parent of parent thread -->
         <div v-if="ancestorThreads.length" class="ancestor-threads">
          <ThreadComponent 
            v-for="thread in ancestorThreads"
            :thread="thread"
            :thread-disabled="true"
            :is-sub-thread="false"
          />
        </div>
        <div class="thread-seperator"></div>
        <!-- current comment-->
        <ThreadComponent
          :thread="parentThread"
          :thread-disabled="true"
          :is-sub-thread="false"
          :parent-to-subthread="ancestorThreads.find((thread) => thread.id === parentThread?.replied_to) || null"
          :selected-comment="true"
          @thread-selected="
            (thread) => {
              clubCommentSelectedForReply = thread
            }
          "
        />
        

        <ClubPostCommentBar
          v-if="clubCommentSelectedForReply"
          :post-id="postData.id"
          :comment="clubCommentSelectedForReply"
          @stop-commenting="clubCommentSelectedForReply = null"
        />
        
        <div class="thread-seperator"></div>

        <div v-if="commentData.length" class="subthread-comment-wrap">
          <ThreadComponent
            v-for="(thread, index) in commentData"
            :key="thread.id"
            :index="index"
            :thread="thread"
            :replying-to-id="clubCommentSelectedForReply?.id || threadId"
            :bookclub-id="bookclub"
            :is-sub-thread="true"
            :parent-to-subthread="parentThread"
            @thread-selected="(thread) => (clubCommentSelectedForReply = thread)"
            @navigating-threads="(threadId) => descendThread(threadId)"
          />
        </div>
        <div class="thread-seperator"></div>
      </template>
      

      <template #loading>
        <div class="loading gradient p-5 text-center fancy">Loading comments</div>
      </template>
    </AsyncComponent>
  </div>
</template>
<script setup lang="ts">
// Vue
import { ref, computed, onMounted } from 'vue'
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

// Params
const route = useRoute()
const router = useRouter()
const { bookclub, postId, threadId } = route.params

// Data refs
const commentData = ref<Array<Thread> | []>([]);
const postData = ref({});
const parentThread = ref<Thread | null>(null);
// Whats before a parent thread, an ancestor thread is all the context from above a subthread.
const ancestorThreads = ref<Thread[]>([]);

/**
 * @load_comments
 */
const GET_COMMENTS_KEY = 'sub-thread-get-comments';
// for comment bar.
const clubCommentSelectedForReply = ref<Thread | null>(null);

// Needed for descending navigationThread gets updated in descendThread.
const navigationThread = ref<String | null>(null);

const computedUrl = computed(() => {
  if (navigationThread.value) {
    return urls.reviews.getCommentForComments(postId, navigationThread.value)
  } else {
    return urls.reviews.getCommentForComments(postId, threadId)
  }
});

async function getCommentsFactory() {
  const ancestorThreadPromiseFactory = () =>  db.get(
    urls.concatQueryParams(
      `${computedUrl.value}/parent_comments`, { book_club_id: bookclub }
    ),
    null, false, (res: any) => {
      ancestorThreads.value = res.data.comments;
    }, (err: any) => {
      console.warn(err);
    }
  );
  
  const threadPromiseFactory = () => db.get(
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
  );

  return Promise.allSettled([ancestorThreadPromiseFactory(), threadPromiseFactory()])
}

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

// Weird bug happening on navigation
// onMounted(() => PubSub.publish(GET_COMMENTS_KEY));
</script>
<style scoped>
.ancestor-threads {
  border-bottom: 1px solid var(--stone-300);
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

.thread-seperator {
  width: 100%;
  padding-top: 20px;
  padding-bottom: 20px;
  border-top: 1px solid var(--stone-300);
  border-bottom: 1px solid var(--stone-300)
}
</style>
