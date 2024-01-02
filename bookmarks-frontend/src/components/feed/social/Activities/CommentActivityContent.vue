<template>
    <div>

    </div>
</template>
<script setup>
    import { onMounted } from 'vue'
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
</script>