<template>
    <div v-if="post.type === ClubUpdatePost.cls" 
        class="post club-update-post"
    >
    <!-- TODO: implement -->
    </div>
    <div v-else-if="post.type === ClubReviewPost.cls"
        class="post club-review-post"
    >
    <!-- TODO: implement -->
    </div>

    <div v-else 
        class="post not-implemented"
    >
        <!-- Other case exception -->
        <h3 class="text-2xl text-stone-600 text-center">
            Something went wrong
        </h3>
    </div>
</template>
<script setup>
import { ClubUpdatePost, ClubReviewPost } from '../../models/models';

const props = defineProps({
    post: {
        type: Object,
        required: true,
    }
});
</script>