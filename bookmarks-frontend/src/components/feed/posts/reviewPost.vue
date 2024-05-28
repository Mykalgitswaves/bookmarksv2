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
            <div v-if="props.book" class="c_c_m_inner mb-0">
                <p class="text-xl font-semibold mb-2 text-indigo-600 cursor-pointer title-hover" 
                    @click="router.push(navRoutes.toBookPageFromPost(user, book.id))"
                >{{ props.book?.title }}</p>

                <img class="review-image" :src="props.book?.small_img_url" alt="">
            </div>

            <!-- What happens if we don't have shit. -->
            <div v-else class="c_c_m_inner">
                <h2 class="text-2xl">No content...</h2>

                <p class="text-slate-500 mt-5">Something weird happened</p>
            </div>
        </div>

        <div class="card-responses">
            <div v-if="headline">
                <div class="divider"></div>            
                <p class="fancy text-xl">{{ headline }}</p>
                <div class="divider"></div>
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
            <div class="flex gap-2">
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

                <button v-if="posted_by_current_user"
                    type="button"
                    class="btn-small icon-btn btn-red-ghost ml-2"
                    @click="setDeletePost(props.id)"
                >
                    <IconTrash />
                    Delete post
                </button>
            </div>
        
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

    <teleport to="body" v-if="deletePostModal[id]"> 
        <form class="modal delete" @submit.prevent="deletePost(id)">
            <h2 class="fancy text-lg text-stone-600">Are you sure you want to delete your post for 
                <br/><span class="text-indigo-500 italic">{{ book.title }}</span>?
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
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { db } from '../../../services/db';
import { urls, navRoutes } from '../../../services/urls';
import { postStore } from '../../../stores/postStore';
import IconLike from '../../svg/icon-like.vue';
import IconComment from '../../svg/icon-comment.vue';
import IconTrash from  '../../svg/icon-trash.vue';
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
    posted_by_current_user: {
        type: Boolean,
        required: true,
    }
});

const router = useRouter();
const route = useRoute();
const _likes = ref(props.likes)
const isLiked = ref(props.liked_by_current_user);
const postLikes = ref(props.likes);
const { user } = route.params;
const emit = defineEmits(['post-deleted']);

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

/**
 * -----------------------------------------------------------------------------------------------
 * DELETING REVIEW POSTS
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
 * END OF DELETING REVIEW POSTS
 * -----------------------------------------------------------------------------------------------
 */


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