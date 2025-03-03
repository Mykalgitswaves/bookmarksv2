<template> 
<section class="post-section-wrapper">
    <createReviewPost 
      v-if="$route.path.includes('review')"
      :headline-error="headlineError"
      :is-postable-data="isPostableData"
      :book-id="bookId"
      @is-postable-data="setPostData" 
      @post-data="postToEndpoint()"
    />

    <createComparisonPost 
      v-if="$route.path.includes('comparison')"
      :is-postable-data="isPostableData"
      :book-id="bookId"
      @is-postable-data="setPostData"
      @set-headlines="setHeadlines"
      @post-data="postToEndpoint()"
    />

    <createUpdatePost 
      v-if="$route.path.includes('update')"
      :is-postable-data="isPostableData"
      :book-id="bookId"
      @is-postable-data="setPostData"
      @post-data="postToEndpoint()"
    />
    <div class="mobile-menu-spacer sm:hidden"></div>
</section>
</template>
<script setup>
// Vue
import { ref, watch, toRaw } from 'vue'; 
import { useRoute, useRouter } from 'vue-router';
// Services
import { urlsMapping } from './createPostService';
import { createQuestionStore } from '../../stores/createPostStore'
import { db } from '@/services/db';
import { navRoutes } from '@/services/urls';
// Components
import createReviewPost from './createPosts/createReviewPost.vue';
import createUpdatePost from './createPosts/createUpdatePost.vue';
import createComparisonPost from './createPosts/createComparisonPost.vue';
import { useToast } from '@/lib/registry/default/ui/toast'

// route macros
const router = useRouter();
const route = useRoute();

const { bookId } = route.params;
const { reviewType } = route.params;
// Refs
const isPostableData = ref(false);
const postTypeMapping = ref('');
const emittedPostData = ref(null);
const { toast } = useToast()

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
    const cleanedData = JSON.parse(JSON.stringify(toRaw(emittedPostData.value)));
    const response = await db.post(urlsMapping[reviewType], cleanedData, true, onSuccess, catchErrors)

    // If response 200's then we're good. Otherwise something funky is a-foot.
    if (response.ok) {
      router.push(navRoutes.toLoggedInFeed(user));  
    } else {
      // Raise error toast here!
      toast({
        title: 'Something weird happened',
        description: 'We are looking into it on our end. \n please report to @michael or @kyle',
      })
    }
}

watch(emittedPostData, () => {
    isPostableData.value = true;
});
</script>
