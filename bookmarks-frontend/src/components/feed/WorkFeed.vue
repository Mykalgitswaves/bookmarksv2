<template>
  <div>
    <div class="flex justify-between">
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
      @click="toggleCreateReviewType = false"
    >
        <IconExit/>
    </button>
    </div>

      <component :is="mapping[postTypeMapping]" :key="postTypeMapping" v-if="toggleCreateReviewType"/>


      <div v-if="!toggleCreateReviewType">
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
import createUpdatePost from './createPosts/createUpdatePost.vue';

// const store = searchResultStore();
const route = useRoute();
const user = route.params.user;
const toggleCreateReviewType = ref(false);
const selectDropdown = ref(false);
const bookData = ref(null);
const postOptions = ['review', 'update', 'comparison'];

const mapping = {
  "review": createReviewPost,
  "update": createUpdatePost
}

async function loadData() {
  if(bookData.value === null) {
    bookData.value = await db.get(urls.booksByN, {'limit': 25}, true)
    console.log('attempting to do this right')
  }
}

onMounted(() => {
    loadData()
})

let postTypeMapping = ref('');

function selectHandler(option) {
  postTypeMapping.value = option;
}

// function cardDelayFn() {
//   if (bookData.value !== null) {
//     return setTimeout(() => {
//       return true
//     }, 500)
//   }
// }

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
</style>