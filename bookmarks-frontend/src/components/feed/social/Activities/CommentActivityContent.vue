<template>
    <div class="activity-comment-blob">
        <p class="text-slate-800 font-medium">{{ actingUserUsername }}</p>
        <p class="activity-comment-text">{{ formattedText }}</p>
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
    import { computed } from 'vue';

    const props = defineProps({
        actingUserId: {
            type: String,
        },
        actingUserProfileImg: {
            type: String,
        },
        actingUserUsername: {
            type: String,
        },
        createdDate: {
            type: Date,
        },
        activityType: {
            type: String,
        },
        postId: {
            type: String,
        },
        bookSmallImgUrls: {
            type: String,
        },
        comment_id: {
            type: String,
        },
        commentText: {
            type: String,
        },
        replyId: {
            type: String,
        },
        replyText: {
            type: String,
        },
        isPinned: {
            type: Boolean,
        }
    });

    const formattedText = computed(() => {
        return `${activityService[props.activityType].string}: "${props.commentText}"`
    })

</script>
<style scoped>

.activity-comment-blob {
    max-width: 600px;
}


.activity-comment-text {
    font-size: var(--font-sm);
    color: var(--slate-600);
    line-break: auto;
}
</style>