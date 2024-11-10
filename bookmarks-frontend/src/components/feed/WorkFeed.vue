<template>
  <div>
    <!-- Your currently reading shown at the top -->
    <div>
      <CurrentlyReading />
    </div>

    <!-- Create posts for feed! -->
    <component 
      v-if="toggleCreateReviewType" 
      :is="mapping[postTypeMapping]" 
      :key="postTypeMapping" 
      @is-postable-data="handlePost"
    />

    <!-- Your actual posts feed -->
    <div v-if="!toggleCreateReviewType" class="reviews">  
      <h2 class="work-feed-heading">Posts</h2>

      <WorkFeedControls :user="user" />

      <TransitionGroup name="content" tag="div">
        <div v-if="feedData?.length" class="cards-outer-wrapper">
          <div
            v-for="post in feedData"
            :key="post.id" 
            class="center-cards"
          >
            <transition name="content" tag="div">
              <component
                v-if="!deletedPosts.includes(post.id)"
                :is="feedComponentMapping[post?.type]?.component()"
                v-bind="feedComponentMapping[post?.type]?.props(post)"
                @post-deleted="hideDeletedPost"
              />
            </transition>
          </div>
        </div>
        <div v-else class="cards-outer-wrapper">
          <div class="center-cards">
            <div class="loading-card gradient">
              <div class="gradient element1"></div>
                
                <div class="gradient element2"></div>
                
                <div class="gradient element3"></div>
                
                
                <div class="gradient element4"></div>
                
                <div class="gradient element5"></div>
            </div>
          </div>
        </div>

        <h2 v-if="feedData?.length" class="mt-10 text-3xl text-stone-700 text-center fancy">No more posts.<br>
          <span class="text-2xl text-indigo-500">Probably a good time to do some reading...📚</span>
        </h2>
      </TransitionGroup>
    </div>
  </div>

  <div class="mobile-menu-spacer sm:hidden"></div>
</template>
<script setup>
import { ref, onMounted, reactive } from 'vue';
import { useRoute } from 'vue-router';
import { db } from '@/services/db.js';
import { urls } from '@/services/urls.js';
import { filterOptions } from './filters.js';
import { navigate } from './createPostService';
import { feedComponentMapping } from './feedPostsService';

import CurrentlyReading from './CurrentlyReading.vue';
import WorkFeedControls from './WorkFeedControls.vue';



const toggleCreateReviewType = ref(false);

const feedData = ref([]);
const privateFeed = ref([]);
const postOptions = ['review', 'update', 'comparison'];
const route = useRoute();
const { user } = route.params; 

function closeModal(reactiveKey) {
  modals[reactiveKey] = false;
}

async function loadWorks() {
    await db.get(urls.reviews.getFeed(), true).then((res) => {
      // We dont want milestone on the feed page since those are private posts.
      feedData.value = res.data.filter((post) => (post.type !== 'milestone' || post.deleted !== true));
      privateFeed.value = res.data.filter((post) => post.type === 'milestone');
    });
}
const deletedPosts = ref([]);

function hideDeletedPost(deletedPostId){
  deletedPosts.value.push(deletedPostId);
}

onMounted(() => {
    loadWorks();
});
</script>
<style scoped>

  .reviews {
    position: relative;
  }


  .card-grids {
    display: grid;
    grid-template-columns: 1;
    row-gap: 1.5rem;
  }

  select {
    width: 100%;
    max-width: 280px;
  }

  .flex-center {
    display: flex;
    align-items: center;
    gap: .5ch;
  }

  .color-white {
    color: #fff;
  }

  /* Animations for stuff */
  .postmapping-move, /* apply transition to moving elements */
  .postmapping-enter-active {
    transition: all 0.5s ease;
  }
  .postmapping-leave-active {
    transition: all 0.5s ease;
  }

  .postmapping-enter-from,
  .postmapping-leave-to {
    opacity: 0;
  }

  /* ensure leaving items are taken out of layout flow so that moving
    animations can be calculated correctly. */
  .postmapping-leave-active {
    position: absolute;
  }

  .cards-leave-active,
  .cards-enter-active {
    transition: all 0.5s ease;
  }
  .cards-enter-from,
  .cards-leave-to {
    opacity: 0;
  }

  .reviews-leave-active,
  .reviews-enter-active {
    transition: all 0.5s ease;
  }
  .reviews-enter-from,
  .reviews-leave-to {
    opacity: 0;
  }

  .border-indigo-600 {
    border-color: #4f46e5;
  }


  /* Loading card */
  .loading-card {
    width: 70vw;
    max-width: 880px;
    height: 550px;
    margin: 16px auto;
    background-color: var(--surface-primary);
    border-radius: var(--radius-md);
    -webkit-box-shadow: var(--shadow-lg);
    -moz-box-shadow: var(--shadow-lg);
    box-shadow: var(--shadow-lg);
  }


  .element1 {
      top: 14%;
      left: 50%;
      transform: translate(-50%, -50%);
      height: 15%;
      width: 50%;
      border-radius: var(--radius-sm)
  }
  .element2 {
      top: 22%;
      left: 80px;
      height: 68px;
      width: 80%;
  }

  .element3 {
      top: 30%;
      left: 16px;
      height: 14px;
      width: 80%;
  }

  .element4 {
      top: 36%;
      left: 16px;
      height: 14px;
      width: 80%;
  }
</style>