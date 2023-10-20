<template>
  <div>
    <div class="flex gap-5">
      <div class="btn-relative">
        <button 
          v-if="postTypeMapping === ''"
          class="flex-center justify-center px-2 py-2 rounded-md color-white bg-indigo-600"
          type="button"
          @click="selectDropdown = !selectDropdown"
        >
          <IconPlus />
          
          <span>Make a Post</span>
          
        </button>
        <button
          v-if="toggleCreateReviewType"
          type="button"
          class="flex-center justify-center px-3 py-2 rounded-md "
          :class="isPostableData ? 'bg-indigo-600 color-white' : 'bg-slate-200 text-slate-600'"
          @click="postToEndpoint()"
        >
          <IconAddPost/>
          Post
        </button>

        <div 
          v-if="selectDropdown" 
          class="popout-flyout shadow-lg"
        >
          <button 
            type="button" 
            v-for="(option, index) in postOptions"
            :key="index"
            @click="selectHandler(option); toggleCreateReviewType = true; selectDropdown = false"  
          >
            {{ option }}
          </button>
        </div>
      </div>
      
      <button 
        v-if="toggleCreateReviewType"
        type="button" 
        class="flex-center justify-center px-2 py-2 bg-red-600 rounded-md color-white" 
        @click="toggleCreateReviewType = false; postTypeMapping = ''"
      >
          <IconExit/>
      </button>
      </div>

      <component 
        v-if="toggleCreateReviewType" 
        :is="mapping[postTypeMapping]" 
        :key="postTypeMapping" 
        @is-postable-data="handlePost"
      />

      <div v-if="!toggleCreateReviewType">
        <p class="pt-4 text-2xl font-medium text-slate-600 mb-5">Reviews</p>

        <TransitionGroup v-if="reviewData" name="reviews" tag="div">
          <ComparisonPost 
            v-for="post in reviewData?.data.Comparison" :key="post"
            :book="post.book"
            :small_img_url="post.book_small_img"
            :headlines="post.book_specific_headlines"
            :book_title="post.book_title"
            :comparisons="post.responses"
            :comparator_ids="post.comparators"
            :created_at="post.created_date"
            :id="post.id"
            :username="post.user_username"
          />

          <ReviewPost
            v-for="post in reviewData?.data.Review" :key="post.id"
            :id="post.id"
            :book="post.book"
            :title="post.book_title"
            :headline="post.headline"
            :question_ids="post.question_ids"
            :questions="post.questions"
            :responses="post.responses"
            :spoilers="post.spoilers"
            :username="post.user_username"
          />
        </TransitionGroup>
        <p class="pt-4 text-2xl font-medium text-slate-600 mb-5">Recommended Works</p>
        
        <KeepAlive>
          <TransitionGroup name="cards" tag="div" class="card-grids">
            <WorkCard 
              v-for="(work, index) in books" 
              :key="index" 
              :work="work"
              :user="user"
            />
          </TransitionGroup>
        </KeepAlive>
      </div>
    </div>
    <div class="mobile-menu-spacer sm:hidden"></div>
</template>
<script setup>
import { ref,  computed, watch, onMounted } from 'vue';
import { useRoute } from "vue-router";
import { db } from '@/services/db.js';
import { urls } from '@/services/urls.js';
import WorkCard from './WorkCard.vue';
import ComparisonPost from './posts/comparisonPost.vue';
import IconPlus from '../svg/icon-plus.vue'
import IconExit from '../svg/icon-exit.vue';
import createReviewPost from './createPosts/createReviewPost.vue';
import createUpdatePost from './createPosts/createUpdatePost.vue';
import createComparisonPost from './createPosts/createComparisonPost.vue';
import ReviewPost from './posts/reviewPost.vue';
import IconAddPost from '../svg/icon-add-post.vue';

// const store = searchResultStore();
const route = useRoute();
const user = route.params.user;
const toggleCreateReviewType = ref(false);
const selectDropdown = ref(false);
const bookData = ref(null);
const reviewData = ref(null);
const isPostableData = ref(false);
const postOptions = ['review', 'update', 'comparison'];

const mapping = {
  "review": createReviewPost,
  "update": createUpdatePost,
  "comparison": createComparisonPost,
}

async function loadWorks() {
    bookData.value = await db.get(urls.booksByN, {'limit': 25}, true);
    reviewData.value = await db.get(urls.reviews.getReviews(user), true);
}


onMounted(() => {
    // loadReviews()
    loadWorks();
    
})

let postTypeMapping = ref('');

function selectHandler(option) {
  postTypeMapping.value = option;
}

let emittedPostData = ref(null);

function handlePost(e) {
  emittedPostData.value = e;
}

const urlsMapping = {
  "review": urls.reviews.review,
  "update": urls.reviews.update,
  "comparison": urls.reviews.comparison,
}


async function postToEndpoint() {
  toggleCreateReviewType.value = false;
  return await db.post(urlsMapping[postTypeMapping.value], emittedPostData, true).then(() => {
    postTypeMapping.value = '';
    // Set to null after request is sent.
    emittedPostData.value = null;
  });
}

const books = computed(() => (bookData.value ? bookData.value.data : ''))

watch(emittedPostData, () => {
  isPostableData.value = true;
})

watch(reviewData, (newV) => {
  console.log(newV)
})

</script>

<style scoped>
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

  
</style>