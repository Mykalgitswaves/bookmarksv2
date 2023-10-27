<template>
    <div>
        <ComparisonPost
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
        />
    </div>
</template>
<script setup>
import { reactive, ref } from 'vue'
import { useRoute } from 'vue-router';
import { urls } from '../../services/urls'; 
import { postStore } from '../../stores/postStore';


import ComparisonPost from './posts/comparisonPost.vue';
// Grab data from and put into a new object so we dont need to load post again
const post = ref(null);
post.value = postStore.state;

// This is for modeling comments and sending to backend
const postData = reactive({});
const route = useRoute();
const { user, comparison } = route.params;

async () => {
    await fetch(urls.reviews.getAllComparisonComments(user, comparison)).then((res) => {
        postData.value = res.data;
    })
}
</script>