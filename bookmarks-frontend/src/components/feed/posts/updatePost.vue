<template>
    <div class="card">
        <!-- Header dude no shit -->
        <div class="card-header">
            <p class="text-slate-600 text-center"
                @click="router.push(navRoutes.toUserPage(route.params.user, user_id))"
            >
                <span class="text-indigo-600 cursor-pointer">{{ props.username }}'s</span>
                made an update: 
            </p>
        </div>

        <div class="card-content-main update">
            <div v-if="book" class="c_c_m_inner">
                <p class="text-xl font-semibold text-indigo-600 cursor-pointer"
                    @click="router.push(navRoutes.toBookPageFromPost(user, book.id))"
                >
                    {{ book.title }}
                </p>

                <img class="review-image" :src="props.book.small_img_url" alt="">

                <h4 class="text-xl italic text-slate-700">
                    on page #<span class="text-indigo-600">{{ page }}</span>
                </h4>
            </div>
            
            <!-- Something weird happened -->
            <div v-else class="c_c_m_inner">
                <h2 class="text-2xl">No content...</h2>

                <p class="text-slate mt-5">Something weird happened</p>
            </div>

            <div v-if="props.headline">
                <div class="divider"></div>

                <p class="fancy text-xl">{{ props.headline }}</p>
                
                <div class="divider"></div>
            </div>

            <div v-if="book && (response || quote)" class="card-responses">
                <!-- Removing headline for now to minimize amount of information people are seeing -->

                <p v-if="quote" class="quote">"{{ quote }}"</p>

                <p v-if="response" class="response">{{ response }}</p>
            </div>
        </div>

        <!-- Footer dawg  -->
        <div class="card-footer">
            <div class="flex gap-2">
                <button
                    type="button"
                    class="text-slate-600 flex items-center"
                    @click="router.push(navRoutes.toPostPageFromFeed(user, props.id))"
                >
                    <IconComment/>
                    <span style="visibility: hidden; width: 0;">{{ num_comments }} comments</span>
                </button>

                <button v-if="posted_by_current_user"
                    type="button"
                    class="btn-small btn-red-ghost"
                    @click="setDeletePost(props.id)"
                >
                    <IconTrash />
                    <span style="visibility: hidden; display: none;">Delete post</span>
                </button>
            </div>

            <button 
                type="button" 
                class="text-slate-600 flex items-center"
                :class="{'is-liked': isLiked}"
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
                <br/><span class="text-indigo-500 italic">{{ book?.title || 'Oops!' }}</span> 
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
import IconComment from '../../svg/icon-comment.vue';
import IconLike from '../../svg/icon-like.vue';
import IconTrash from  '../../svg/icon-trash.vue';
import { urls, navRoutes } from '../../../services/urls.js';
import { db } from '../../../services/db.js';
import { createConfetti } from '../../../services/helpers.js';

const props = defineProps({
    book: {
        type: Number,
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
    quote: {
        type: String,
        required: false,
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
    user_id: {
        type: String,
        required: true
    },
    num_comments: {
        type: Number,
        required: true
    },
    likes: {
        type: Number,
        required: true
    },
    liked_by_current_user: {
        type: Boolean,
        required: true
    },
    posted_by_current_user: {
        type: Boolean,
        required: true,
    },
});

const isLiked = ref(props.liked_by_current_user);
const _likes = ref(props.likes);
const emit = defineEmits(['post-deleted']);
const router = useRouter();
const route = useRoute();
const { user } = route.params

async function AddLikeOrUnlike(){
    let url = isLiked.value ? 
        urls.reviews.unlikePost(props.id) :
        urls.reviews.likePost(props.id);
    // Turning off debug for now.
    await db.put(url, false).then(() => {
        isLiked.value = !isLiked.value;
        isLiked.value ? _likes.value += 1 : _likes.value -= 1;
    });
    
    // Make it fun right?
    if(isLiked.value){
        await createConfetti();
    }

}

/**
 * -----------------------------------------------------------------------------------------------
 * DELETING UPDATE POSTS
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
 * END OF DELETING UPDATE POSTS
 * -----------------------------------------------------------------------------------------------
 */
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