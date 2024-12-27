<template>
  <div>
    <div>
      <AsyncComponent :promises="[clubsPromise]">
        <template #resolved>
            <div style="margin-left: 16px;">
              <h2 class="text-stone-600 text-2xl fancy">Bookclubs you own</h2>

              <p class="text-stone-500 text-sm italic pl-5">Your most recently active bookclubs</p>
            </div>
            <div v-if="bookclubs?.ownedByUser?.length" 
                class="mb-5 mt-5 bookclubs-gallery"
            > 
              <!-- Only show three -->
                <BookClubPreview 
                    v-for="bookclub in bookclubs.ownedByUser.slice(0,3)"
                    :bookclub="bookclub"
                    :user="user"
                />

                <!-- In case there are more than three load a button in the toolbar to view all! -->
                <div v-if="bookclubs.ownedByUser.length > 2">
                  <RouterLink 
                    class="btn btn-tiny btn-nav text-sm fancy"
                    :to="navRoutes.toBookClubsPage(user)"
                  >
                    View all
                  </RouterLink>
                </div>
            </div>
        </template>

        <template #loading>
          <div style="margin-left: 16px;">
              <h2 class="text-stone-600 text-2xl fancy">Bookclubs you own</h2>

              <p class="text-stone-500 text-sm italic pl-5">Your most recently active bookclubs</p>
            </div>

          <div class="currently-reading">
              <div class="currently-reading-book loading">
                  <div class="book-img loading gradient"></div>
              </div>

              <div class="currently-reading-book loading">
                  <div class="book-img loading gradient"></div>
              </div>

              <div class="currently-reading-book loading">
                  <div class="book-img loading gradient"></div>
              </div>

              <div class="currently-reading-book loading">
                  <div class="book-img loading gradient"></div>
              </div>
          </div>
        </template>  
      </AsyncComponent>

    </div>
    
    <!-- Your currently reading shown at the top -->
    <div class="mt-5 mb-10">
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
      <div style="margin-left: 16px;">
        <h2 class="text-stone-600 text-2xl fancy">Community library</h2>

        <p class="text-stone-500 text-sm italic pl-5">A collection of posts from you and your friends</p>
      </div>

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
import { useRoute, useRouter } from 'vue-router';
import { db } from '@/services/db.js';
import { urls, navRoutes } from '@/services/urls.js';
import { filterOptions } from './filters.js';
import { navigate } from './createPostService';
import { feedComponentMapping } from './feedPostsService';
import AsyncComponent from '@/components/feed/partials/AsyncComponent.vue';
import BookClubPreview from '@/components/feed/bookclubs/home/BookClubPreview.vue';

import CurrentlyReading from './CurrentlyReading.vue';
import WorkFeedControls from './WorkFeedControls.vue';


const toggleCreateReviewType = ref(false);

const feedData = ref([]);
const privateFeed = ref([]);
const postOptions = ['review', 'update', 'comparison'];
const route = useRoute();
const { user } = route.params; 

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

/**
 * @bookclubs_promises
 */
const bookclubs = ref({
  ownedByUser: [],
  joinedByUser: []
});

const clubsOwnedByUserFactory = () =>db.get(urls.bookclubs.getClubsOwnedByUser(user), null, false, (res) => {
  bookclubs.value.ownedByUser = res.bookclubs;
});

const clubsJoinedByUserFactory = () => db.get(urls.bookclubs.getClubsJoinedByCurrentUser(user), null, false, (res) => {
  bookclubs.value.joinedByUser = res.bookclubs;
});

const clubsPromise = Promise.allSettled([clubsOwnedByUserFactory(), clubsJoinedByUserFactory()]);

/**
 * @end_bookclubs_promises
 */
loadWorks();
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

  .bookclubs-gallery {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    row-gap: 1.5rem;
    padding: 16px;
    column-gap: 1.5rem;
    border-radius: var(--radius-md);
    border: 1px solid var(--stone-200);
  }

  @media screen and (max-width: 768px) {
    .bookclubs-gallery {
      grid-template-columns: 1fr;
    }
  }

  @starting-style {
    .currently-reading {
      opacity: 0;
    }
  }
  
  .currently-reading {
        --x-axis-offset: 24px;
        --height: fit-content;
        @media screen and (max-width: 768px) {
            --x-axis-offset: 14px;
        }
        transition: all 250ms ease-in-out;
        margin-top: var(--margin-sm);
        margin-bottom: var(--margin-sm);
        margin-left: auto;
        margin-right: auto;
        display: flex;
        column-gap: var(--margin-md);
        justify-content: start;
        height: var(--height);
        overflow-x: scroll;
        overflow-y: visible;
        padding-left: var(--x-axis-offset);
        transition: var(--transition-short);
        -ms-overflow-style: none;  /* IE and Edge */
        scrollbar-width: none;
        border: 1px solid var(--stone-200);
        border-radius: var(--radius-md);
    }

    .currently-reading::-webkit-scrollbar {
        display: none;
    }

    .currently-reading-book {
        --min-width-cr-card: 300px;
        min-width: var(--min-width-cr-card);
        font-family: var(--fancy-script);
        text-align: center;
        position: relative;
        border: 1px solid var(--surface-primary);
        background-color: var(--surface-primary);
        padding: 10px;

        .book-metadata {
            display: flex;
            align-items: start;
            justify-content: space-between;
            padding-left: var(--margin-sm);
            padding-right: var(--margin-sm);
            
            .book-title {
                font-size: var(--font-xl);
            }

            .progress {
                color: var(--indigo-700);
                font-weight: 600;
                position: absolute;
                top: 10px;
                left: 10px;
            }
        }

        .book-img {
            border-radius: var(--radius-md);
            width: 100%;
            height: 240px;
            object-fit: scale-down;
            margin-bottom: 8px;
            border: 4px solid var(--hover-container-gradient);

            &.loading{  
                background-color: var(--stone-200);
                height: 300px;
            }
        }
    }

    .currently-reading-book:not(:has(.gradient)):hover {
        background-color: var(--stone-50);
        border-radius: var(--radius-md);
        cursor: pointer;
        transition: background-color 350 ease-in-out;
    }
</style>