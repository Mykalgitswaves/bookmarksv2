<template>
  <div>
    <div class="flex gap-5 space-between">
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


        <div class="btn-relative">
          <button
            v-if="!toggleCreateReviewType"
            type="button"
            class="flex-center justify-center px-2 py-2 bg-indigo-100 text-indigo-600 rounded-md"
            @click="filterPopout = !filterPopout"
          >
              <IconFilter />
              Filter
          </button>
          
          <div
            v-if="filterPopout"
            class="popout-right shadow-lg px-2 py-2"
          >
            <div 
              v-for="(option, index) in filterOptions" 
              :key="index"
              class="is_ai my-2"
            >
              <label
                :for="index + '-option'"
                
              >
                <input 
                  type="checkbox" 
                  name="" 
                  :id="option.pk + '-option'"
                  v-model="option.is_active"
                  :value="true"
                />
                {{ option.filter }}
              </label>
            </div>
          </div>
        </div>
      </div>

      <component 
        v-if="toggleCreateReviewType" 
        :is="mapping[postTypeMapping]" 
        :key="postTypeMapping" 
        @is-postable-data="handlePost"
      />

      <div v-if="!toggleCreateReviewType">

        <TransitionGroup v-if="reviewData" name="reviews" tag="div">
          <div v-if="!filterOptions[0].is_active" class="center-cards">
            <ComparisonPost 
              v-for="post in reviewData?.data.Comparison"
              :key="post.id"
              :book="post.book"
              :small_img_url="post.book_small_img"
              :headlines="post.book_specific_headlines"
              :book_title="post.book_title"
              :comparisons="post.responses"
              :comparators="post.comparators"
              :comparator_ids="post.comparators"
              :created_at="post.created_date"
              :id="post.id"
              :username="post.user_username"
              :likes="post.likes"
            />
          </div>

          <div v-if="!filterOptions[1].is_active" class="center-cards">
            <ReviewPost
              v-for="post in reviewData?.data.Review" 
              :key="post.id"
              :id="post.id"
              :book="post.book"
              :title="post.book_title"
              :headline="post.headline"
              :question_ids="post.question_ids"
              :questions="post.questions"
              :responses="post.responses"
              :spoilers="post.spoilers"
              :username="post.user_username"
              :small_img_url="post.book_small_img"
              :likes="post.likes"
            />
          </div>
          <div v-if="!filterOptions[2].is_active" class="center-cards">
            <UpdatePost
              v-for="post in reviewData?.data.Update" 
              :key="post.id"
              :id="post.id"
              :book="post.book"
              :title="post.book_title"
              :headline="post.headline"
              :response="post.response"
              :spoiler="post.spoiler"
              :username="post.user_username"
              :small_img_url="post.book_small_img"
              :page="post.page"
              :likes="post.likes"
            />
          </div>
        </TransitionGroup>
      </div>
    </div>

    <div class="mobile-menu-spacer sm:hidden"></div>
</template>
<script setup>
import { ref,  computed, watch, onMounted } from 'vue';
import { useRoute } from "vue-router";
import { db } from '@/services/db.js';
import { urls } from '@/services/urls.js';
import { filterOptions } from './filters.js';
import ComparisonPost from './posts/comparisonPost.vue';
import ReviewPost from './posts/reviewPost.vue';
import UpdatePost from './posts/updatePost.vue';
import IconPlus from '../svg/icon-plus.vue'
import IconExit from '../svg/icon-exit.vue';
import IconFilter from '../svg/icon-filter.vue';
import createReviewPost from './createPosts/createReviewPost.vue';
import createUpdatePost from './createPosts/createUpdatePost.vue';
import createComparisonPost from './createPosts/createComparisonPost.vue';
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
const filterPopout = ref(false);

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

  .border-indigo-600 {
    border-color: #4f46e5;
  }
  
</style>