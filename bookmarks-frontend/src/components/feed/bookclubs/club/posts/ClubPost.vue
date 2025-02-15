<template>
    <div v-if="post.type === ClubUpdatePost.cls">
        <div class="card club" :class="{'post-liked-by-user': isLikedByCurrentUser}">
            <!-- Header dude no shit -->
            <div class="card-header">
                <p class="text-slate-600 text-center"
                >
                <!-- @click="router.push(navRoutes.toUserPage(route.params.user, user_id))" -->
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

                    <p class="fancy text-xl">{{ post.headline }}</p>
                    
                    <div class="divider"></div>
                </div>

                <div v-if="post.response.length" class="card-responses">
                    <!-- Removing headline for now to minimize amount of information people are seeing -->

                    <p v-if="post.quote" class="quote">"{{ post.quote }}"</p>

                    <p v-if="post.response" class="response">{{ post.response }}</p>
                </div>
            </div>

            <!-- Footer dawg  -->
            <div class="card-footer">
                <!-- Rethink these as club specific controls. -->
                    <!-- todo add in n more awards stuff here. -->
                <div class="flex items-center">
                    <button 
                        type="button"
                        title="like post"
                        class="btn btn-tiny btn-icon mr-auto btn-specter relative b-0 m-r-5" 
                        :class="{'liked': isLikedByCurrentUser}"
                        style="height: 48px; width: 48px;"
                        @click="likeOrUnlikeClubPost"
                    >
                        <IconClubLike />

                        <span v-if="likes > 0" 
                            class="like-count"
                        >
                            {{ likes }}
                        </span>
                    </button>

                    <button 
                        v-if="!isViewingPost"
                        type="button"
                        title="comment"
                        class="btn btn-tiny btn-icon mr-auto btn-specter b-0" 
                        @click="router.push(navRoutes.toBookClubCommentPage(user, bookclub, post.id))"
                    >
                        <IconComment />
                    </button>
                </div>
                
                <div :class="{'expanded': false}">
                    <button 
                        type="button"
                        title="view awards"
                        class="btn btn-tiny btn-icon mr-auto btn-specter b-0" 
                        @click="dispatchAwardEvent(post)"
                    >
                        <IconAwards />
                    </button>
                </div>
            </div>
        </div>

        <div class="awards-list" v-if="awards.length">
            <div
                v-for="(award, index) in awards" 
                :key="award.id" 
            >
                <div v-if="award.num_grants > 0" 
                    class="award"
                    :class="{'granted-by-user': award.granted_by_current_user}"
                    :title="award.name"
                    @click="grantOrUngrantAward(award, index - 1)"
                >
                    <span>
                        <span class="num-grants">{{ award.num_grants }}</span>
                        <component v-if="ClubAwardsSvgMap[award.cls]" :is="ClubAwardsSvgMap[award.cls]()"/>
                    </span>
                </div>
            </div>
        </div>
        <!-- 
            If you are not previewing the post in feed that 
            means you are on the post page, but if youre on the post
            page we are calling clubcomments separately
         -->
        <div v-if="!isViewingPost && !!post.comments?.length">
            <ClubComment
                :is-preview="true" 
                :comment-data="helpersCtrl.firstOrNone(post.comments)"
                :url-to-comment-page="navRoutes.toBookClubCommentPage(user, bookclub, post.id)"
            />
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

    <Teleport to="body">
        <Transition name="content">
            <SuccessToast
                v-if="toast" 
                :toast="toast" 
                :toast-type="Toast.TYPES.MESSAGE_TYPE" 
                @dismiss="() => toast = null"
            /> 
        </Transition>
    </Teleport>
</template>
<script setup>
import { urls, navRoutes } from '../../../../../services/urls';
import { helpersCtrl } from '../../../../../services/helpers';
import { db } from '../../../../../services/db';
import { ClubUpdatePost, ClubReviewPost } from '../../models/models';
import { ClubAwardsSvgMap } from '../awards/awards';
import { computed, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import IconComment from '../../../../svg/icon-club-comment.vue';
import IconAwards from '../awards/icons/Awards.vue';
import IconClubLike from '../awards/icons/ClubLike.vue';
import SuccessToast from '../../../../shared/SuccessToast.vue';
import { Toast } from '../../../../shared/models';
import { PubSub } from '../../../../../services/pubsub';
import CommentBar from './comments/CommentBar.vue';
import ClubComment from './comments/ClubComment.vue';

const props = defineProps({
    post: {
        type: Object,
        required: true,
    },
    isViewingPost: {
        type: Boolean,
        required: false,
        default: false,
    }
});

console.log(props.post.id)

const awardsRef = ref(
    Object.entries(props.post.awards).map(([key, award]) => {
        award.id = key;
        return award;
    })
);

const route = useRoute();
const router = useRouter();
const { bookclub, user } = route.params;
const toast = ref(null); 

/**
 * @typedef { awards} – Returns a list containing the first 4 awards sorted
 *  in descending order first, then either false in the case that there are no remaining awards, 
 * or a Number indicating how many more award types have been granted on this post.
 * @param {awards}
 * @returns {List[list, (Number | Bool)]}
 */
const awards = computed(() => {
    return awardsRef.value.sort((a, b) => b.num_grants - a.num_grants);
});


function dispatchAwardEvent(post) {
    PubSub.publish('open-award-post-modal', {
        post_id: post.id
    });
};

function successDeleteFunction(award, vForIndex) {
    // Either way wipe out existing toast
    toast.value = null;
    toast.value = { 
        message: `Ungranted award: ${award.name}`,
        isDeletion: true,
    };

    if (award.num_grants > 1) {
        award.num_grants -= 1;
        award.granted_by_current_user = false;
    } else {
        award.num_grants -= 1;
        award.granted_by_current_user = false;
    };
}


function successGrantFunction(award, vForIndex) {
    // Either way wipe out existing toast
    toast.value = null;
    toast.value = {
        message: `Granted award: ${award.name}`
    };

    award.num_grants += 1;
    award.granted_by_current_user = true;
}


/**
 * @description function for granting or deleting awards from posts.
 * @param award 
 * @param vForIndex 
 */
function grantOrUngrantAward(award, vForIndex) {
    // did we grant? if not grant.
    if (!award.granted_by_current_user) {
        db.put(urls.bookclubs.grantAwardToPost(route.params.bookclub, props.post.id, award.id), 
            null,
            false, 
            successGrantFunction(award, vForIndex),
            (err) => console.log(err),
        );
    } else {
        db.delete(urls.bookclubs.ungrantAwardToPost(route.params.bookclub, props.post.id, award.id), 
            null,
            false, 
            successDeleteFunction(award, vForIndex), 
            (err) => console.log(err),
        );
    }
};

// Make each post subscribe to an awards channel.
PubSub.subscribe(`award-granted-to-${props.post.id}`, (award) => {
    award.num_grants = 1;
    awardsRef.value.push(award);
});

// ---------------------------------------------------------------
// ---------------------------------------------------------------
// Likes
// ---------------------------------------------------------------
// ---------------------------------------------------------------

const likes = ref(props.post.likes);
const isLikedByCurrentUser = ref(props.post.liked_by_current_user);

function likeOrUnlikeClubPost() {
    let url = !isLikedByCurrentUser.value ? 
        urls.reviews.likePost(props.post.id) :
        urls.reviews.unlikePost(props.post.id);

    db.put(url, null, false, () => {
        if (!isLikedByCurrentUser.value) {
            likes.value += 1;
            isLikedByCurrentUser.value = true;
        } else {
            likes.value -= 1;
            isLikedByCurrentUser.value = false;
        }   
    }, (err) => {
        console.error(err);
    });
};
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

.awards-list {
    margin-bottom: -10px;
    margin-right: 10px;
    margin-left: 10px;
    display: flex;
    flex-direction: row;
    column-gap: 4px;
    row-gap: 4px;
    justify-content: start;
    flex-wrap: wrap;
    background-color: var(--surface-primary);
    border: 1px solid var(--slate-400);
    border-radius: var(--radius-sm);
    padding: 6px 8px;

    .award {
        position: relative;
        height: 40px;
        width: 40px;
        color: var(--indigo-500);
        border: 1px solid var(--indigo-600);
        border-radius: 4px;
        fill: var(--indigo-500);

        &:hover {
            /* Make a new hover state if you are going to remove an award vs grant one.
                Can be red for removing, green for granting
            */
            background-color: var(--indigo-50) !important;
            border: 1px solid var(--indigo-400);
        }

        &.granted-by-user {
            background-color: var(--indigo-100);
            fill: var(--indigo-600);
        }
    }

    @media screen and (max-width: 768px) {
        .award {
            height: 50px;
            width: 50px;
        }
    }
}

.num-grants {
    position: absolute;
    top: -12px;
    left: -4px;
    padding: 4px 8px;
    border-radius: 4px;
    background-color: var(--stone-700);
    color: var(--stone-50);
    text-align: center;
    z-index: 2;
    line-height: 1;
    font-size: var(--font-xs);
}

.liked {
    color: var(--red-500) !important;
    fill: var(--red-500) !important;
}

.like-count {
    position: absolute;
    z-index: 10px;
    top: -5px;
    right: 0;
    font-family: var(--fancy-script);
    font-size: var(--font-xs);
    font-weight: bold;
    padding: 2px 4px;
    background-color: var(--red-100);
    color: var(--red-500);
    border-radius: 2px;
}
</style>