<template>
    <div class="card">
        <div class="card-header">
            <p class="text-slate-600 text-center">
                <span class="text-indigo-600 cursor-pointer">{{ props.username }}'s</span>
                made an update: 
            </p>
        </div>

        <div class="card-content-main">
            <div class="c_c_m_inner">
                <img class="review-image" :src="props.small_img_url" alt="">
                <p class="text-xl font-semibold my-2 text-indigo-600">{{ props.title }}</p>
                <p v-if="props.headline.length" class="fancy text-2xl">{{ props.headline }}</p>
            </div>
        </div>

        <div class="card-responses">
                    <div class="divider"></div>
                    
                    <div class="text-slate-600 my-2 justify-self items-center">
                        <IconBrain/>    
                    </div>

                    <h3 class="text-3xl text-indigo-600 italic mb-5">{{ props.page }}</h3>

                   <p>{{ props.response }}</p>
                </div>

        <div class="card-footer">
            <button
                type="button"
                class="text-slate-600 flex items-center"
                @click="navigateToCommentPage()"
            >
                <IconComment/>
                <span class="ml-2">comments</span>
            </button>
        
            <button 
                type="button" 
                class="text-slate-600 flex items-center"
                :class="{'is-liked': isLiked}"
                @click="isLiked = !isLiked"
            >
                <IconLike/>
                <span class="ml-2">Like</span>
            </button>
        </div>
    </div>    
</template>
<script setup>
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import IconComment from '../../svg/icon-comment.vue';
import IconLike from '../../svg/icon-like.vue';

const props = defineProps({
    book: {
        type: Number,
        required: true,
    },
    title: {
        type: String,
        required: true,
    },
    response: {
        type: String,
        required: true,
    },
    spoilers: {
        type: Array,
        required: true,
    },
    page: {
        type: Number,
        required: true,
    },
    username: {
        type: String,
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
    }
});

const isLiked = ref(false);

const router = useRouter();
const route = useRoute();

const { user } = route.params

function navigateToCommentPage() {
    router.push(`/feed/${user}/post/${props.id}`);
}
</script>