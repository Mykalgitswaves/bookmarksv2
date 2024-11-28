<template>
    <div v-if="post.type === ClubUpdatePost.cls">
        <div class="card club">
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
                <button 
                    class="btn btn-tiny btn-icon mr-auto btn-specter b-0" 
                    @click="dispatchAwardEvent(post.id)"
                >
                    <IconAwards />
                </button>
                
                <div class="awards-list" :class="{'expanded': false}" v-if="awards.length">
                    <div v-for="(award, index) in awards" 
                        :key="award.id" 
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
import { urls } from '../../../../../services/urls';
import { db } from '../../../../../services/db';
import { ClubUpdatePost, ClubReviewPost } from '../../models/models';
import { ClubAwardsSvgMap } from '../awards/awards';
import { computed, ref } from 'vue';
import {useRoute} from 'vue-router';
import IconAwards from '../awards/icons/Awards.vue';

const props = defineProps({
    post: {
        type: Object,
        required: true,
    }
});

const awardsRef = ref(Object.values(props.post.awards));
const awardsCount = 
awardsRef.value.forEach((award) => {
    award.count = award.granted_by_current_user ? 1 : 0;
});

const route = useRoute();

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

function dispatchAwardEvent(postId) {
    const event = new CustomEvent('open-award-post-modal', {
        detail:  {
            post_id: postId
        }
    });
    window.dispatchEvent(event);
};


function grantOrUngrantAward(award, vForIndex) {
    // did we grant? if not grant.
    if (!award.granted_by_current_user) {
        db.put(urls.bookclubs.grantAwardToPost(route.params.bookclub, props.post.id, award.id), 
            null, 
            false, 
            () => {
                award.num_grants += 1;
                award.granted_by_current_user = true;
            },
            (err) => {
                console.log(err);
            }
        );
    } else {
        db.delete(urls.bookclubs.ungrantAwardToPost(route.params.bookclub, props.post.id), 
            {cls: award.cls}, 
            false, 
            () => {
                if (award.num_grants > 1) {
                    award.num_grants -= 1;
                    award.granted_by_current_user = false;
                } else {
                    award.num_grants -= 1;
                    award.granted_by_current_user = false;
                    awardsRef.splice(1, vForIndex, index + 1);
                };
            }, (err) => {
                console.log(err);
            }
        );
    }
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
    margin-right: -20px;
    display: flex;
    column-gap: 4px;
    row-gap: 4px;
    justify-content: start;
    flex-wrap: wrap;
    background-color: var(--surface-primary);

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
</style>