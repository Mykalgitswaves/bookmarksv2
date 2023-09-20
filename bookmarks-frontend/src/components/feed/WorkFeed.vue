<template>
  <div class="relative">
    <div>
      <button 
        class="flex-center justify-center px-2 py-2 rounded-md color-white"
        :class="(!toggleCreateReviewType ? 'bg-indigo-600' : 'bg-red-600')"
        type="button"
        @click="toggleCreateReviewType = !toggleCreateReviewType"
      >
        <IconPlus v-if="!toggleCreateReviewType"/>
        <IconExit v-if="toggleCreateReviewType"/>
        <span v-if="!toggleCreateReviewType">Make a Post</span>
      </button>

      <TransitionGroup name="postmapping" tag="div">
        <div v-if="toggleCreateReviewType">
          <div>
            <label for="post-options" class="font-medium text-slate-600 mt-5 mb-2 block">Creating a:</label>

            <select
              class="px-6 py-2 text-lg rounded-md border-indigo-300 border-2 border-solid"
              name="post-options" 
              id="post-options"
              @change="selectHandler"
            >
              <option 
                v-for="(post, index) in postOptions"
                :key="index"
                :value="post">
                {{ post }}
              </option>
            </select>
          </div>
        
          <component :is="mapping[postTypeMapping]" :key="postTypeMapping"/>
        
        </div>
      </TransitionGroup>
    </div>
    
    <TransitionGroup name="postmapping" tag="div">
      <div v-if="!toggleCreateReviewType">
        <p class="pt-4 text-2xl font-medium text-slate-600 mb-5">Recommended Works</p>

        <div class="card-grids">
          <WorkCard 
            v-for="(work, index) in books" 
            :key="index" 
            :work="work"
            :user="user"
          />
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>
<script setup>
import { ref, toRaw, computed, watch, onMounted } from 'vue';
import { useRoute } from "vue-router";
import { db } from '@/services/db.js';
import { urls } from '@/services/urls.js';
import { postData } from '../../../postsData.js'
import { searchResultStore } from '@/stores/searchBar.js'
import WorkCard from './WorkCard.vue';
import IconPlus from '../svg/icon-plus.vue'
import IconExit from '../svg/icon-exit.vue';
import createReviewPost from './createPosts/createReviewPost.vue';

// const store = searchResultStore();
const route = useRoute();
const user = route.params.user;
const toggleCreateReviewType = ref(false);
const bookData = ref(null);
const postOptions = ['review', 'update', 'comparison']

const mapping = {
  "review": createReviewPost,
}

async function loadData() {
  bookData.value = await db.get(urls.booksByN, {'limit': 25}, true)
  console.log('attempting to do this right')
}

onMounted(() => {
    loadData()
})

let postTypeMapping = 'review';

function selectHandler(e) {
  console.log(e.target.value)
  postTypeMapping = e.target.value;
}

const books = computed(() => (bookData.value ? bookData.value.data : ''))

watch(bookData.value, (oldValue, newValue) => {
  console.log(newValue, oldValue, 'watching watching watching')
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

.postmapping-move, /* apply transition to moving elements */
.postmapping-enter-active {
  transition: all 0.4s ease;
}
.postmapping-leave-active {
  transition: all 0.25s ease;
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
</style>