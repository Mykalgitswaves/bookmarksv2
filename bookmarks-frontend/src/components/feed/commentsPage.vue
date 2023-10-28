<template>
    <div>
        
    </div>
</template>
<script setup>
import { reactive, ref } from 'vue'
import { useRoute } from 'vue-router';
import { urls } from '../../services/urls'; 
import { db } from '../../services/db';
import { postStore } from '../../stores/postStore';


import ComparisonPost from './posts/comparisonPost.vue';
import UpdatePost from './posts/updatePost.vue';
import ReviewPost from './posts/ReviewPost.vue';



// Grab data from and put into a new object so we dont need to load post again

// This is for modeling comments and sending to backend
const postData = reactive({});
const route = useRoute();
const { user, post } = route.params;
console.log(route.params)

async function get_post() {
    await db.get(urls.reviews.getPost(user, post)).then((res) => {
        postData.value = res.data;
    });
}
get_post();

/* <ComparisonPost
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
        /> */
</script>