<template>
    <div>
        
    </div>
</template>
<script setup>
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