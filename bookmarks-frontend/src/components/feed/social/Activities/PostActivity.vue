<template>
        <div>
            <p class="text-slate-800 font-medium">{{ actingUserUsername }}</p>
            <p class="text-slate-600 t-base">{{ activityService[activityType].string }}</p>
        </div>

        <div class="activity-book-images"
            @click="activityService[activityType].click(route.params.user, postId, router)"
        >
            <img 
                v-for="(img, index) in bookSmallImgUrls"
                :key="index"
                class="activity-book-image"
                :src="img"
                alt=""
            >
        </div>
</template>
<script setup>
    import { activityService } from './activityMapping'; 
    import { useRouter, useRoute } from 'vue-router';

    const router = useRouter();
    const route = useRoute();
    const props = defineProps({
        actingUserId: {
            type: String
        },
        actingUserProfileImg: {
            type: String
        },
        actingUserUsername: {
            type: String
        },
        createdDate: {
            type: Date
        },
        activityType: {
            type: String
        },
        postId: {
            type: String
        },
        bookSmallImgUrls: {
            type: String
        }
    });
</script>
