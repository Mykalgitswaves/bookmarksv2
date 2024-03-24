<template>
<div class="card" 
    :class="{'card-is-liked': isLiked || props.liked_by_current_user}"
>
    <div class="card-header">
        <p class="text-slate-600 text-center"
            @click="router.push(navRoutes.toUserPageFromPost(route.params.user, props.user_id))"
        >
            <span class="text-indigo-600 cursor-pointer">{{ username }}'s</span>
            made a review: 
        </p>
    </div>

        <div class="card-content-main">
            <!-- Happy case -->
            <div v-if="props.book" class="c_c_m_inner">
                <img class="review-image" :src="props.book?.small_img_url" alt="">

                <p class="text-xl font-semibold my-2 text-indigo-600 cursor-pointer title-hover" 
                    @click="router.push(navRoutes.toBookPageFromPost(user, book.id))"
                >{{ props.book?.title }}</p>

                <p v-if="headline" class="fancy text-2xl">{{ headline }}</p>
            </div>

            <!-- What happens if we don't have shit. -->
            <div v-else class="c_c_m_inner">
                <h2 class="text-2xl">No content...</h2>

                <p class="text-slate-500 mt-5">Something weird happened</p>
            </div>
        </div>

        <div class="card-responses">
            <div class="divider"></div>
            
            <div class="text-slate-600 my-2 justify-self items-center">
                <IconBrain/>
            </div>

            <ul class="my-3 content-start">
                <li v-for="(r, index) in props.responses" 
                    :key="index"
                    class="card-commonalities"
                >
                
                    <h3>{{ props.questions[index] }}</h3>
                    
                    <p class="mt-2 ml-2 text-slate-500">{{ r }}</p>
                </li>  
            </ul>
        </div>

        <div class="card-footer">
            <button
                type="button"
                class="text-slate-600 flex items-center"
                @click="navigateToCommentPage()"
            >
                <IconComment/>
                
                <span class="ml-2">
                    {{ num_comments }} comments
                </span>
            </button>
        
            <button type="button" 
                class="text-slate-600 flex items-center"
                :class="{'is-liked': isLiked}"
                @click="AddLikeOrUnlike()"
            >
                <IconLike/>

                <span class="ml-2">{{ _likes }} likes</span>
            </button>
        </div>
    </div> 
</template>
<script setup>
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { db } from '../../../services/db';
import { urls, navRoutes } from '../../../services/urls';
import { postStore } from '../../../stores/postStore';
import IconLike from '../../svg/icon-like.vue';
import IconComment from '../../svg/icon-comment.vue';
import IconBrain from '../../svg/icon-brain.vue';
import { createConfetti } from '../../../services/helpers.js';

const props = defineProps({
    book: {
        type: Object,
        required: true,
    },
    responses: {
        type: Array,
        required: true,
    },
    questions: {
        type: Array,
        required: true
    },
    spoilers: {
        type: Array,
        required: true,
    },
    username: {
        type: String,
        required: true,
    },
    likes: {
        type: Number,
        required: false,
    },
    question_ids: {
        type: Array,
        required: true,
    },
    headline: {
        type: String,
        required: false,
        default: () => 'Not too much thought',
    },
    id: {
        type: Number,
        required: true
    },
    num_comments: {
        type: Number,
        required: true,
    },
    user_id: {
        type: String,
        required: true
    },
    deleted: {
        type: Boolean,
        required: true,
    },
    liked_by_current_user: {
        type: Boolean,
        required: true,
    },
});

const router = useRouter();
const route = useRoute();
const _likes = ref(props.likes)
const isLiked = ref(props.liked_by_current_user);
const postLikes = ref(props.likes);
const { user } = route.params;


async function AddLikeOrUnlike(){
    let url = isLiked.value ? 
        urls.reviews.unlikePost(props.id) :
        urls.reviews.likePost(props.id);
    // Turning off debug for now.
    await db.put(url, false).then(() => {
        isLiked.value = !isLiked.value;
        isLiked.value ? _likes.value += 1 : _likes.value -= 1;
    });

    if (isLiked.value) {
        await createConfetti();
    }
}

function navigateToCommentPage() {
    // Not sure we need this here but doing it elsewhere so fuck it.
    postStore.save(props.id);
    router.push(navRoutes.toPostPageFromFeed(user, props.id));
}
</script>
<style scoped>
.justify-self {
    display: flex;
    justify-content: center;
}

.review-image {
    transition: 250ms ease;
    border-radius: 4px;
}
.review-image:hover {
    transform: translateY(-5%) rotateX(15deg) translateZ(0);
    box-shadow: 2px 35px 32px -8px rgba(0, 0, 0, 0.25);
    -webkit-box-shadow: 2px 35px 32px -8px rgba(0, 0, 0, 0.25);
    -moz-box-shadow: 2px 35px 32px -8px rgba(0, 0, 0, 0.25);
}

.title-hover {
    transition: 250ms ease;
}

.title-hover:hover {
    color: #312e81;
}
</style>