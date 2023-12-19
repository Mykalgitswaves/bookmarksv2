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
            @click="
              selectHandler(option);
              toggleCreateReviewType = true;
              selectDropdown = false
            "  
          >
            {{ option }}
          </button>
        </div>
      </div>
      
      <button 
        v-if="toggleCreateReviewType"
        type="button" 
        class="flex-center justify-center px-2 py-2 bg-red-600 rounded-md color-white" 
        @click="
          toggleCreateReviewType = false; 
          postTypeMapping = ''
        "
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
              <label :for="index + '-option'">
                <input 
                  type="checkbox"
                  :id="option.pk + '-option'"
                  v-model="option.is_active"
                  :value="false"
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
        <TransitionGroup name="content" tag="div">
          <div v-if="feedData && loaded">
            <div
              v-for="(post, index) in feedData"
              :key="index" 
              class="center-cards"
            >
              <component
                :is="feedComponentMapping[post?.type]?.component()"
                v-bind="feedComponentMapping[post?.type]?.props(post)"
              />
            </div>
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
import { feedComponentMapping } from './feedPostsService';
import IconPlus from '../svg/icon-plus.vue'
import IconExit from '../svg/icon-exit.vue';
import IconFilter from '../svg/icon-filter.vue';
import createReviewPost from './createPosts/createReviewPost.vue';
import createUpdatePost from './createPosts/createUpdatePost.vue';
import createComparisonPost from './createPosts/createComparisonPost.vue';
import IconAddPost from '../svg/icon-add-post.vue';
import ComparisonPost from './posts/comparisonPost.vue';
import ReviewPost from './posts/reviewPost.vue';
import UpdatePost from './posts/updatePost.vue';


// const store = searchResultStore();
const route = useRoute();
const user = route.params.user;
const toggleCreateReviewType = ref(false);
const selectDropdown = ref(false);
const bookData = ref(null);
const feedData = ref(null);
const loaded = ref(false)
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
    await db.get(urls.reviews.getFeed(), true).then((res) => {
      feedData.value = res.data.filter((d) => d.type !== 'milestone');
    });
}

onMounted(() => {
    // loadReviews()
    loadWorks();
    
});

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

watch(feedData, (newV) => {
  if(newV) {
    loaded.value = true
  }
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