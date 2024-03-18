<template>
    <div class="card">
        <!-- Username of OP -->
        <div class="card-header">
            <p  class="text-slate-600"
                @click="router.push(navRoutes.toUserPageFromPost(route.params.user, props.user_id))"
            >
                <span class="text-indigo-600 underline italic cursor-pointer">
                    @{{ props.username }}</span> made a comparison
            </p>
        </div>

        <div class="card-content-main">
            <!-- headings for comparisons -->
            <div v-if="book?.length" class="comparisons">
                <div class="comparison">
                    <img class="comparison-image" :src="small_img_url?.length ? small_img_url[0] : ''" alt="">
                    <p  class="text-xl font-semibold cursor-pointer title-hover" 
                        @click="router.push(navRoutes.toBookPageFromPost(user, book[0]))"
                    >{{ props.book_title[0] }}</p>
                    <p class="comparison-headline">{{ headlines[0] }}</p>
                </div>

                <IconLinkArrow />

                <div class="comparison">
                    <img class="comparison-image" 
                        :src="small_img_url?.length ? small_img_url[1] : ''" 
                        alt=""
                    >
                    
                    <p class="text-xl font-semibold cursor-pointer title-hover"
                        @click="router.push(navRoutes.toBookPageFromPost(user, book[1]))"
                    >{{ props.book_title[1] }}</p>
                    
                    <p v-if="headlines?.length && headlines[1]?.length" 
                       class="comparison-headline"
                    >{{ headlines[1] }}</p>
                </div>
            </div>

            <!-- Error case if some content doesn't load with the initial request. -->
            <div v-else>
                <h2 class="text-2xl">No content...</h2>

                <p class="text-slate-500 mt-5">Something weird happened</p>
            </div>
        </div>

        <!-- Actual comparisons dude -->
        <div v-if="comparisons?.length" class="card-responses">
            <div class="divider"></div>

            <h3 class="text-slate-700 text-lg my-2">Commonalities</h3>

            <ul class="my-3 content-start">
                <li 
                    v-for="(c, index) in comparisons" 
                    :key="index"
                    class="card-commonalities"
                >
                
                    <h3>{{ comparators[index] }}</h3>
                    
                    <p class="mt-2 ml-2 text-slate-500">{{ c }}</p>
                </li>  
            </ul>
        </div>

        <!-- Actions -->
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
                @click="AddLikeOrUnlike(id)"
            >
                <IconLike/>
                <span class="ml-2">Like</span>
            </button>
        </div>
    </div>
</template>
<script setup>
import IconLinkArrow from '../../svg/icon-arrow-link.vue';
import IconLike from '../../svg/icon-like.vue';
import IconComment from '../../svg/icon-comment.vue';
import { postStore } from '../../../stores/postStore';
import { reactive, ref, } from 'vue';
import { db } from '../../../services/db';
import { urls, navRoutes } from '../../../services/urls';
import { useRoute, useRouter } from 'vue-router'

const props = defineProps({
    book: {
        type: Array,
        required: true
    },
    book_title: {
        type: Array,
        required: true,
    },
    small_img_url: {
        type: Array,
        required: true
    },
    headlines: {
        type: Array,
        required: false,
    },
    comparisons: {
        type: Array,
        required: true
    },
    comparators: {
        type: Array,
        required: true
    },
    comparator_ids: {
        type: Array,
        required: true
    },
    createdAt: {
        type: String,
        required: true,
    },
    username: {
        type: String,
        required: true,
    },
    id: {
        type: String,
        required: true,
    },
    isIronic: {
        type: Boolean,
        required: false,
        default: false,
    },
    isAiGeneratedHeadlines: {
        type: Boolean,
        required: false,
        default: false
    },
    user_id: {
        type: String,
        required: true
    },
    likes: {
        type: Number
    }
})

const showReview = reactive({});
showReview[props.id] = false;

const isLiked = ref(null);
const route = useRoute();
const router = useRouter();
const user = route.params.user;

async function AddLikeOrUnlike(id){
    const user_id = route.params.user;
    // Turning off debug for now.
    await db.post(
        urls.reviews.likeComparison(user_id, id), false
    ).then(() => {
        isLiked.value = true;
    });
}

function navigateToCommentPage() {
    postStore.save(props.id);
    router.push(navRoutes.toPostPageFromFeed(user, props.id));
}

</script>
<style scoped>

.v-enter-active,
.v-leave-active {
  transition: opacity 0.5s ease;
}

.v-enter-from,
.v-leave-to {
  opacity: 0;
}
</style>