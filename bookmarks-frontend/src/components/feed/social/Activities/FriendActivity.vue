<template>
    <div class="activity-comment-blob">
        <p class="friends-comment-text"><span class="username">{{ current_username}}</span> {{ formattedText }} <span class="username">{{ actingUserUsername }}</span></p>
    </div>

    <div
        @click="activityService[activityType].click(route.params.user, actingUserId, router)"
    >
        <img 
            v-if="actingUserProfileImg"
            class="small-profile-image"
            :src="actingUserProfileImg"
            alt=""
        >
    </div>
</template>
<script setup>
import { activityService } from './activityMapping';
import {computed } from 'vue';

    const props = defineProps({
        current_username: {
            type: String,
        },
        actingUserId: {
            type: String,
        },
        actingUserProfileImg: {
            type: String,
        },
        actingUserUsername: {
            type: String,
        },
        activityType: {
            type: String,
        },
        createdDate: {
            type: Date,
        }
    })

    const formattedText = computed(() => {
        return activityService[props.activityType].string
    })
</script> 
<style scoped>
.username {
    color: var(--slate-800);
    font-weight: 500;
    cursor: pointer;
}
.friends-comment-text {
    color: var(--slate-600);
}
</style>