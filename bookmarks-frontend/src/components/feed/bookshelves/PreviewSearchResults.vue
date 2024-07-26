<template>
    <div v-if="postPreviews?.length" class="post-previews">
        <div v-for="post in postPreviews" 
            :key="post.id"
            class="preview-post"
        >
            <div class="post-meta">
                <h3 v-if="post.headline" class="text-lg text-stone-700">{{ post.headline }}</h3>
                <h3 v-else class="text-lg text-stone-600"> No headline</h3>
                
                <p class="text-sm text-stone-500">created on {{ dates.dateAtTime(post.created_date) }}</p>
            </div>

            <a :href="postURl(post.id)" class="btn btn-small btn-ghost">
                view post
            </a>
        </div>
    </div>

    <div v-else class="text-center ml-auto mr-auto mt-5 mb-10">
        <h3 class="text-stone-500 fancy text-xl">No updates <span class="text-2xl">🫥</span></h3>
    </div>
</template>
<script setup>
import { dates } from '../../../services/dates';
import { useRoute } from 'vue-router';
import { navRoutes } from '../../../services/urls';

const props = defineProps({
    bookId: {
        type: String,
        required: true,
    },
    postPreviews: {
        type: Array,
        required: true,
    },
});

const route = useRoute();
const { user } = route.params;

function postURl(postId){
    return navRoutes.toPostPageFromFeed(user, postId)
}
</script>
<style scoped>
.post-previews {
    display: grid;
    row-gap: 8px;
    grid-template-columns: 1fr;
    margin-top: 8px;
}

.preview-post {
    width: 100%;
    display: flex;
    justify-content: space-between;
    padding: 14px var(--padding-sm);
    border-radius: var(--radius-sm);
    border: 1px solid var(--stone-300);
}
</style>