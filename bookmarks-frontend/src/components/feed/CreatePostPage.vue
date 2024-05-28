<template> 
<section class="post-section-wrapper">
    <BackBtn />  

    <createReviewPost 
      v-if="reviewType === 'review'"
      :is-postable-data="isPostableData"
      @is-postable-data="setPostData" 
      @post-data="postToEndpoint()"
    />

    <createComparisonPost 
      v-if="reviewType === 'comparison'"
      :is-postable-data="isPostableData"
      @is-postable-data="setPostData"
      @set-headlines="setHeadlines"
      @post-data="postToEndpoint()"
    />

    <createUpdatePost 
      v-if="reviewType === 'update'"
      :is-postable-data="isPostableData"
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
async function postToEndpoint() {
    await db.post(urlsMapping[reviewType], emittedPostData, true).then(() => {
      postTypeMapping.value = '';
      // Set to null after request is sent.
      emittedPostData.value = null;
      store.clearQuestions();
      router.push({name: 'home-feed', params: { user: route.params.user }})
  });
}

watch(emittedPostData, () => {
    isPostableData.value = true;
});
</script>
