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
            <div v-if="bookBlobs?.length" class="comparisons">
                <div class="comparison">
                    <p  class="text-xl font-semibold cursor-pointer title-hover" 
                        @click="router.push(navRoutes.toBookPageFromPost(user, bookBlobs[0]?.id))"
                    >{{ bookBlobs[0]?.title }}</p>

                    <img class="comparison-image" :src="bookBlobs[0]?.small_img_url ? bookBlobs[0].small_img_url : ''" alt="">

                    <p class="comparison-headline">{{ headlines[0] }}</p>
                </div>

                <IconLinkArrow />

                <div class="comparison">
                    <p class="text-xl font-semibold cursor-pointer title-hover"
                        @click="router.push(navRoutes.toBookPageFromPost(user, bookBlobs[1]?.id))"
                    >{{ bookBlobs[1]?.title }}</p>

                    <img class="comparison-image" :src="bookBlobs[1]?.small_img_url ? bookBlobs[1]?.small_img_url : ''" alt="">
                    
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
            
            <h3 class="text-slate-700 text-xl my-2 fancy">Commonalities</h3>
            
            <div class="divider"></div>
            
            <ul class="my-3 content-start">
                <li 
                    v-for="(c, index) in comparisons" 
                    :key="index"
                    class="card-commonalities"
                >
                
                    <h3>{{ comparators[index] }}</h3>
                    
                    <p class="mt-2 ml-2 card-commonality-response">{{ c }}</p>
                </li>  
            </ul>
        </div>

        <!-- Actions -->
        <div class="card-footer">
            <div class="flex gap-2">
                <button
                    type="button"
                    class="text-slate-600 flex items-center"
                    @click="navigateToCommentPage()"
                >
                    <IconComment/>
                    <span class="ml-2">{{ num_comments }} comments</span>
                </button>
                
                <button v-if="posted_by_current_user"
                    type="button"
                    class="btn-small icon-btn btn-red-ghost ml-2"
                    @click="setDeletePost(props.id)"
                >
                    <IconTrash />
                    Delete post
                </button>
            </div>
            
        
            <button 
                type="button" 
                class="text-slate-600 flex items-center"
                :class="{ 'is-liked': isLiked }"
                @click="AddLikeOrUnlike()"
            >
                <IconLike/>
                <span class="ml-2">{{ _likes }} Likes</span>
            </button>
        </div>
    </div>
    <teleport to="body" v-if="deletePostModal[id]"> 
        <form class="modal delete" @submit.prevent="deletePost(id)">
            <h2 class="fancy text-lg text-stone-600">Are you sure you want to delete your comparison post for 
                <br/><span class="text-indigo-500 italic">{{ bookBlobs[0]?.title || 'Oops!' }}</span> 
                <br/>&
                <br/><span class="text-indigo-500 italic">{{ bookBlobs[1]?.title || 'Oops! something weird happened' }}</span>?
            </h2>

            <div class="flex items-center justify-center gap-5 mt-5">
                <button
                    type="submit"
                    class="btn btn-red"
                >Delete</button>
    
                <button type="button"
                    class="btn btn-ghost"
                    @click="deletePostModal[id] = false;"
                >
                    Cancel
                </button>
            </div>
        </form>
    </teleport>
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
import { createConfetti } from '../../../services/helpers';
import IconTrash from  '../../svg/icon-trash.vue';

const props = defineProps({
    bookBlobs: {
        type: Array,
        required: true,
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
    createdDate: {
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
    },
    liked_by_current_user: {
        type: Boolean,
        required: true
    },
    num_comments: {
        type: Number,
        required: true
    },
    posted_by_current_user: {
        type: Boolean,
        required: true,
    }
});

const showReview = reactive({});
showReview[props.id] = false;

const _likes = ref(props.likes);
const isLiked = ref(props.liked_by_current_user);
const route = useRoute();
const router = useRouter();
const user = route.params.user;
const emit = defineEmits(['post-deleted']);

async function AddLikeOrUnlike(){
    let url = isLiked.value ? 
        urls.reviews.unlikePost(props.id) :
        urls.reviews.likePost(props.id);
    console.log(url);
    // Turning off debug for now.
    await db.put(url, false).then(() => {
        isLiked.value = !isLiked.value;
        isLiked.value ? _likes.value += 1 : _likes.value -= 1;
    });

    if(isLiked.value) {
        await createConfetti();
    }
}

function navigateToCommentPage() {
    postStore.save(props.id);
    router.push(navRoutes.toPostPageFromFeed(user, props.id));
}

/**
 * -----------------------------------------------------------------------------------------------
 * DELETING COMPARISON POSTS
 * -----------------------------------------------------------------------------------------------
 */
// We want to prompt users to make sure they are confident in deleting. hence the additional steps.
const deletePostModal = ref({});

// See above, this is so we dont open every modal at once.
function setDeletePost(id) {
    deletePostModal.value[id] = true;
}
// The actual delete function.
async function deletePost(id){
    await db.delete(urls.reviews.deletePost(id)).then(() => {
        deletePostModal.value[id] = false;
        emit('post-deleted', id);
    });
}
/**
 * -----------------------------------------------------------------------------------------------
 * END OF DELETING COMPARISON POSTS
 * -----------------------------------------------------------------------------------------------
 */

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