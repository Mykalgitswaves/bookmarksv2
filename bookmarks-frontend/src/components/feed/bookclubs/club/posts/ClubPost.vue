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
                <div class="ml-auto text-end">
                    <div class="awards-list" :class="{'expanded': false}" v-if="awards.length">
                        <div v-for="award in awards" 
                            :key="award.id" 
                            class="award"
                            :class="{'granted-by-user': award.granted_by_current_user}"
                            :title="award.name"
                            @click="ungrantAward(award.id, award.granted_by_current_user)"
                        >
                            <component v-if="ClubAwardsSvgMap[award.cls]" :is="ClubAwardsSvgMap[award.cls]()"/>
                        </div>
                    </div>
                    
                    <span v-if="awards[1]"></span>

                    <!-- todo add in n more awards stuff here. -->
                    <button 
                        class="btn btn-tiny text-indigo-500 underline mr-auto" 
                        @click="dispatchAwardEvent(post.id)"
                    >
                        View all awards
                    </button>
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
import { ClubUpdatePost, ClubReviewPost } from '../../models/models';
import { ClubAwardsSvgMap } from '../awards/awards';
import { computed } from 'vue';

const props = defineProps({
    post: {
        type: Object,
        required: true,
    }
});

/**
 * @typedef { awards} – Returns a list containing the first 4 awards sorted
 *  in descending order first, then either false in the case that there are no remaining awards, 
 * or a Number indicating how many more award types have been granted on this post.
 * @param {awards}
 * @returns {List[list, (Number | Bool)]}
 */
const awards = computed(() => {
    const _awards = Object.values(props.post.awards);
    return _awards.sort((a, b) => b.num_grants - a.num_grants);
});

function dispatchAwardEvent(postId) {
    const event = new CustomEvent('open-award-post-modal', {
        detail:  {
            post_id: postId
        }
    });
    window.dispatchEvent(event);
};

function ungrantAward() {

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
    border: 1px solid red; 
    margin-bottom: -10px;
    margin-right: -20px;
    display: flex;
    column-gap: 4px;
    row-gap: 4px;
    justify-content: start;
    flex-wrap: wrap;
    background-color: var(--surface-primary);

    .award {
        height: 40px;
        width: 40px;
        color: var(--indigo-500);
        border: 1px solid var(--stone-100);
        border-radius: 4px;
        fill: var(--indigo-500);

        &:hover {
            background-color: var(--indigo-50);
            border: 1px solid var(--indigo-400);
        }

        &.granted-by-user {
            background-color: var(--green-100);
            fill: var(--);
        }
    }

    @media screen and (max-width: 768px) {
        .award {
            height: 50px;
            width: 50px;
        }
    }
}
</style>