<template>
    <transition-group tag="div" name="content">
        <div v-if="postType === 'ComparisonPost'" class="center-cards">
            <ComparisonPost 
              :book="p.book"
              :small_img_url="p.book_small_img"
              :headlines="p.book_specific_headlines"
              :book_title="p.book_title"
              :comparisons="p.responses"
              :comparators="p.comparators"
              :comparator_ids="p.comparators"
              :created_at="p.created_date"
              :id="p.id"
              :username="p.user_username"
            />
          </div>

          <div v-if="postType === 'ReviewPost'" class="center-cards">
            <ReviewPost
              :id="p.id"
              :book="p.book"
              :title="p.book_title"
              :headline="p.headline"
              :question_ids="p.question_ids"
              :questions="p.questions"
              :responses="p.responses"
              :spoilers="p.spoilers"
              :username="p.user_username"
              :small_img_url="p.book_small_img"
            />
          </div>
          <div v-if="postType === 'UpdatePost'" class="center-cards">
            <UpdatePost
              :id="p.id"
              :book="p.book"
              :title="p.book_title"
              :headline="p.headline"
              :response="p.response"
              :spoiler="p.spoiler"
              :username="p.user_username"
              :small_img_url="p.book_small_img"
              :page="p.page"
            />
          </div>
          <Comments v-if="p?.comments" :comments="p.comments"/>
          <div class="mobile-menu-spacer sm:hidden"></div>
    </transition-group>
</template>
<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router';
import { urls } from '../../services/urls'; 
import { db } from '../../services/db';
import { postStore } from '../../stores/postStore';
import Comments from './posts/comments.vue';
import ComparisonPost from './posts/comparisonPost.vue';
import UpdatePost from './posts/updatePost.vue';
import ReviewPost from './posts/ReviewPost.vue';

// Grab data from and put into a new object so we dont need to load post again

// This is for modeling comments and sending to backend
const p = ref(null);
const postType = ref('');

const route = useRoute();
const { user, post } = route.params;

async function get_post() {
    await db.get(urls.reviews.getPost(user, post)).then((res) => {
        p.value = res.data.post;
        postType.value = res.data.post_type;
    });
}
get_post();

</script>
