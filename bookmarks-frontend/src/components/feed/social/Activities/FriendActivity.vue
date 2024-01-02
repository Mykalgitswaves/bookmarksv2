<template>
    <div>
        Friend ship activities dude.
    </div>
</template>
<script setup>
    import { watchEffect } from 'vue';

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
        activityType: {
            type: String,
        },
        createdDate: {
            type: Date,
        }
    })
</script> 