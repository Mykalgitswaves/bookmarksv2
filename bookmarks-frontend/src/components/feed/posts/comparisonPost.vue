<template>
    <div class="card">
        <div class="card-header">
            <p class="text-slate-600"><span class="text-indigo-600 underline italic cursor-pointer">@{{ props.username }}</span> made a comparison</p>
        </div>
        <div class="card-content-main">
            <div class="comparisons">
                <div class="comparison">
                    <img class="comparison-image" :src="props.small_img_url[0]" alt="">
                    <p class="text-xl font-semibold">{{ props.book_title[0] }}</p>
                    <p class="comparison-headline">{{ props.headlines[0][0] }}</p>
                </div>

                <IconLinkArrow />

                <div class="comparison">
                    <img class="comparison-image" :src="props.small_img_url[1]" alt="">
                    <p class="text-xl font-semibold">{{ props.book_title[1] }}</p>
                    <p class="comparison-headline">{{ props.headlines[0][1] }}</p>
                </div>
            </div>
        </div>

        <div class="card-responses">
            <div class="divider"></div>

            <h3 class="text-slate-700 text-lg my-2">Commonalities</h3>

            <ul class="my-3 content-start">
                <li 
                    v-for="(c, index) in props.comparisons" 
                    :key="index"
                    class="card-commonalities"
                >
                
                    <h3>{{ props.comparators[index][0] }}</h3>
                    
                    <p class="mt-2 ml-2 text-slate-500">{{ c[0] }}</p>
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
                <span class="ml-2">comments</span>
            </button>
        
            <button 
                type="button" 
                class="text-slate-600 flex items-center"
                :class="{'is-liked': isLiked}"
                @click="AddLikeOrUnlike(props.id)"
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
import { urls } from '../../../services/urls';
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
    }
})

const showReview = reactive({});
showReview[props.id] = false;

const isLiked = ref(null);
const route = useRoute();
const router = useRouter();
const user = route.params.user;

async function AddLikeOrUnlike(id){
    const user_id = route.params.user
    await db.post(
        urls.reviews.likeComparison(user_id, id), true
        )
        .then((res) => {
            console.log(res)
            isLiked.value = true;
        });
}

function navigateToCommentPage() {
    postStore.save(props);
    router.push(`/feed/${user}/comparison/${props.id}`);
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