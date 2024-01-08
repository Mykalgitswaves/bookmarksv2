<template>
  <div>
    <div class="flex gap-5">
      <div class="btn-relative">
        <button 
          class="flex-center justify-center px-2 py-2 rounded-md color-white bg-indigo-600"
          type="button"
          @click="selectDropdown = !selectDropdown"
        >
          <IconPlus />
          
          <span>Make a Post</span>
          
        </button>

        <div 
          v-if="selectDropdown" 
          class="popout-flyout shadow-lg"
        >
          <button 
            type="button" 
            v-for="(option, index) in postOptions"
            :key="index"
            @click="navigate(createPostBaseRoute, option)"  
          >
            {{ option }}
          </button>
        </div>
      </div>


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
          <div v-if="feedData?.length">
            <div
              v-for="post in feedData" :key="post.id" 
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
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { db } from '@/services/db.js';
import { urls } from '@/services/urls.js';
import { filterOptions } from './filters.js';
import { feedComponentMapping } from './feedPostsService';
import IconPlus from '../svg/icon-plus.vue'
import IconExit from '../svg/icon-exit.vue';
import IconFilter from '../svg/icon-filter.vue';
import { navigate } from './createPostService';
const toggleCreateReviewType = ref(false);
const selectDropdown = ref(false);
const bookData = ref(null);
const feedData = ref(null);
const postOptions = ['review', 'update', 'comparison'];
const filterPopout = ref(false);
const route = useRoute();
const { user } = route.params; 
const createPostBaseRoute = `/feed/${user}/create`;

async function loadWorks() {
    bookData.value = await db.get(urls.booksByN, {'limit': 25}, true);
    await db.get(urls.reviews.getFeed(), true).then((res) => {
      feedData.value = res.data.filter((d) => d.type !== 'milestone');
    });
}

onMounted(() => {
    loadWorks();
});
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