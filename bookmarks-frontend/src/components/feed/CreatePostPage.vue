<template> 
<section class="post-section-wrapper">
    <BackBtn/>    
    <component
        :is="componentMapping[reviewType]"
        @is-postable-data="handlePost"
    />

    <button 
        v-if="isPostableData"
        type="button"
        class="post-btn"
        @click="postToEndpoint()"
    >
        <IconAddPost/>
        post
    </button>

    <div class="mobile-menu-spacer sm:hidden"></div>
</section>
</template>
<script setup>
import { ref, watch } from 'vue';
import { componentMapping, urlsMapping} from './createPostService';
import { useRoute, useRouter } from 'vue-router';
import { db } from '../../services/db';
import IconAddPost from '../svg/icon-add-post.vue';
import BackBtn from './partials/back-btn.vue';

const isPostableData = ref(false);
const postTypeMapping = ref('');
const emittedPostData = ref(null);
const router = useRouter();
const route = useRoute();
const { reviewType } = route.params

function handlePost(e) {
  emittedPostData.value = e;
}

async function postToEndpoint() {
    await db.post(urlsMapping[reviewType], emittedPostData, true).then(() => {
    postTypeMapping.value = '';
    // Set to null after request is sent.
    emittedPostData.value = null;
    router.push({name: 'home-feed', params: { user: route.params.user }})
  });
}

watch(emittedPostData, () => {
  isPostableData.value = true;
});
</script>

<style scoped>
.post-btn {
    max-width: 880px;
    display: flex;
    width: 100%;
    justify-content: center;
    align-items: center;
    margin-top: calc(2 * var(--margin-md));
    padding: var(--padding-sm);
    border-radius: var(--radius-sm);
    color: var(--surface-primary);
    background-color: var(--indigo-500);
}

</style>