<template>
    <div class="activity">
        <img v-if="activity?.profile_img_url" class="small-profile-image" src="" alt="">
        <placeholder v-else class="small-profile-image"/>
        
        <div class="activity-content">
            <p>{{ activity?.acting_user_username }}</p>

        </div>
            <component
                :is="activityMap[type].component" 
                v-bind="activityMap[type].props(activity)" 
            />
    </div>
</template>
<script setup>
    import placeholder from '../../../svg/placeholderImage.vue';
    import { activityMap, getFormattedActivityType } from './activityMapping';
    import { computed } from 'vue';

    const props = defineProps({
        activity: {
            type: Object,
            required: true,
        }
    });

    const type = computed(() => {
        return getFormattedActivityType(props.activity.activity_type);
    });
</script>
<style scoped>
    .activity {
        display: flex;
        flex-direction: row;
        padding: 12px;
    }
</style>