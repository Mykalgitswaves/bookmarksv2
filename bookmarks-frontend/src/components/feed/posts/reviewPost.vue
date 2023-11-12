<template>
<div class="card" :class="{'card-is-liked': isLiked || props.liked_by_current_user}">
        <div class="card-header">
            <p class="text-slate-600 text-center">
                <span class="text-indigo-600 cursor-pointer">{{ props.username }}'s</span>
                made a review: 
            </p>
        </div>

        <div class="card-content-main">
            <div class="c_c_m_inner">
                <img class="review-image" :src="props.small_img_url" alt="">
                <p 
                    class="text-xl font-semibold my-2 text-indigo-600 cursor-pointer" 
                    @click="router.push(`/feed/${user}/works/${props.book}`)"
                >{{ props.title }}</p>
                <p v-if="props.headline.length" class="fancy text-2xl">{{ props.headline }}</p>
            </div>
        </div>

        <div class="card-responses">
                    <div class="divider"></div>
                    
                    <div class="text-slate-600 my-2 justify-self items-center">
                        <IconBrain/>
                        
                    </div>

                    <ul class="my-3 content-start">
                        <li 
                            v-for="(r, index) in props.responses" 
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
                    {{ props.num_comments }} comments
                </span>
            </button>
        
            <button 
                type="button" 
                class="text-slate-600 flex items-center"
                :class="{'is-liked': isLiked}"
                @click="likePost()"
            >
                <IconLike/>
                <span class="ml-2">{{ postLikes }} likes</span>
            </button>
        </div>
    </div> 
</template>
<script setup>
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { db } from '../../../services/db';
import { urls } from '../../../services/urls';
import IconLike from '../../svg/icon-like.vue';
import IconComment from '../../svg/icon-comment.vue';
import IconBrain from '../../svg/icon-brain.vue';

const props = defineProps({
    book: {
        type: Number,
        required: true,
    },
    title: {
        type: String,
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
    small_img_url: {
        type: String,
        required: true
    },
    liked_by_current_user: {
        type: Boolean,
        required: true,
    },
    num_comments: {
        type: Number,
        required: true,
    }
});

const isLiked = ref(false);
const postLikes = ref(props.likes);

const router = useRouter();
const route = useRoute();
console.log(props.book)
const { user } = route.params

async function likePost() {
    isLiked.value = !isLiked.value;
    if(isLiked.value === true) {
        await db.put(urls.reviews.likePost(props.id), null, true).then(() => {
            postLikes.value += 1;
        })
    } else {
        await db.put(urls.reviews.unlikePost(props.id), null, true).then(() => {
            postLikes.value -= 1;
        })
    }
}

function navigateToCommentPage() {
    router.push(`/feed/${user}/post/${props.id}`);
}
</script>
<style scoped>
.justify-self {
    display: flex;
    justify-content: center;
}
</style>