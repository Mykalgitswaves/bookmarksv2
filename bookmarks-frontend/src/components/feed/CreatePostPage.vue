<template> 
<section class="post-section-wrapper">
    <BackBtn />  

    <createReviewPost 
      v-if="reviewType === 'review'"
      :headline-error="headlineError"
      :is-postable-data="isPostableData"
      :book_id="bookId"
      @is-postable-data="setPostData" 
      @post-data="postToEndpoint()"
    />

    <createComparisonPost 
      v-if="reviewType === 'comparison'"
      :is-postable-data="isPostableData"
      :book_id="bookId"
      @is-postable-data="setPostData"
      @set-headlines="setHeadlines"
      @post-data="postToEndpoint()"
    />

    <createUpdatePost 
      v-if="reviewType === 'update'"
      :is-postable-data="isPostableData"
      :book_id="bookId"
      @is-postable-data="setPostData"
      @post-data="postToEndpoint()"
    />
    <div class="mobile-menu-spacer sm:hidden"></div>
</section>
</template>
<script setup>

import createReviewPost from './createPosts/createReviewPost.vue';
import createUpdatePost from './createPosts/createUpdatePost.vue';
import createComparisonPost from './createPosts/createComparisonPost.vue';
import { ref, watch, toRaw } from 'vue'; 
import { urlsMapping } from './createPostService';
import { createQuestionStore } from '../../stores/createPostStore'
import { useRoute, useRouter } from 'vue-router';
import { db } from '../../services/db';
import IconAddPost from '../svg/icon-add-post.vue';
import BackBtn from './partials/back-btn.vue';


const isPostableData = ref(false);
const postTypeMapping = ref('');
const emittedPostData = ref(null);
const router = useRouter();
const route = useRoute();
const bookId = route.params.bookID || null; // Default to null if not provided
const { reviewType } = route.params

function setHeadlines(e){
  if (emittedPostData.value) {
    emittedPostData.value['book_specific_headlines'] = toRaw(e);
  }
}

function setPostData(e) {
  emittedPostData.value = e;
}
// Make sure to clear out questions on successfull post.
const store = createQuestionStore();
const headlineError = ref(null);

async function catchErrors(error){
  if (error.status === 400){
    // Parse error.detail
    const errorDetail = JSON.parse(error.detail);
    // Check if errorDetail is an array
    if (Array.isArray(errorDetail)) {
      errorDetail.forEach((e) => {
        // Display the error message on page
        if (e.loc[0] === "responses"){
          let index = e.loc[1];
          let question = store.arr[index];
          question.error = e.msg;
          store.addOrUpdateQuestion(question)
        }
        else if (e.loc[0] === "headline"){
          headlineError.value = e.msg;
        }
      });
    }
    else {
      // Display the error message on page
      // errors.value.push(errorDetail);
    } 
  }
}

async function onSuccess(){
  postTypeMapping.value = '';
  // Set to null after request is sent.
  emittedPostData.value = null;
  store.clearQuestions();
  router.push({name: 'home-feed', params: { user: route.params.user }})
}

async function postToEndpoint() {
    await db.post(urlsMapping[reviewType], emittedPostData, true, onSuccess, catchErrors)
}

watch(emittedPostData, () => {
    isPostableData.value = true;
});
</script>
