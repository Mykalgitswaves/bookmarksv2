<template>
    <div v-if="post.type === ClubUpdatePost.cls">
        <div class="card club">
            <!-- Header dude no shit -->
            <div class="card-header">
                <p class="text-slate-600 text-center"
                >
                <!-- @click="router.push(navRoutes.toUserPageFromPost(route.params.user, user_id))" -->
                    <span class="text-indigo-600 cursor-pointer">{{ post.user_username }}'s</span>
                    made an update: 
                </p>
            </div>

            <div class="card-content-main update">
                <div v-if="post.book" class="c_c_m_inner">
                    <p class="text-xl font-semibold text-indigo-600 cursor-pointer"
                    >
                    <!-- @click="router.push(navRoutes.toBookPageFromPost(user, book.id))" -->
                        {{ post.book.title }}
                    </p>

                    <img class="review-image" :src="post.book.small_img_url" alt="">

                    <h4 class="text-xl italic text-slate-700">
                        chapter <span class="text-indigo-600">{{ post.chapter }}</span>
                        <!-- on page #<span class="text-indigo-600">{{ post.page }}</span> -->
                    </h4>
                </div>
                
                <!-- Something weird happened -->
                <div v-else class="c_c_m_inner">
                    <h2 class="text-2xl">No content...</h2>

                    <p class="text-slate mt-5">Something weird happened</p>
                </div>

                <div v-if="post.headline">
                    <div class="divider"></div>

                    <p class="fancy text-xl">{{ props.headline }}</p>
                    
                    <div class="divider"></div>
                </div>

                <div v-if="post.book && (post.response || post.quote)" class="card-responses">
                    <!-- Removing headline for now to minimize amount of information people are seeing -->

                    <p v-if="quote" class="quote">"{{ post.quote }}"</p>

                    <p v-if="response" class="response">{{ post.response }}</p>
                </div>
            </div>

            <!-- Footer dawg  -->
            <div class="card-footer">
                <!-- Rethink these as club specific controls. -->
                <div class="flex gap-2">
                </div>

               
            </div>
        </div>
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
<style scoped>
.quote {
    padding-left: var(--padding-md);
    padding-right: var(--padding-md);
    padding-top: var(--spacing-sm);
    padding-bottom: var(--spacing-sm);
    margin-bottom: var(--spacing-sm);
    margin-right: var(--spacing-md);
    margin-left: var(--spacing-md);
    font-style: italic;
    background-color: var(--stone-50);
    color: var(--stone-800);
    border-radius: var(--radius-sm);
}

.response {
    padding-left: var(--padding-md);
    padding-right: var(--padding-md);
}

.response::first-letter {
    font-size: var(--font-2xl);
    font-family: var(--fancy-script);
    font-optical-sizing: auto;
    font-weight: 500;
}
</style>