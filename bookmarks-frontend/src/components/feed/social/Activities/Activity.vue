<template>
    <div class="activity">
        <img v-if="activity?.profile_img_url" class="small-profile-image" src="" alt="">
        
        <placeholder v-else class="small-profile-image"/>
        
        <div class="activity-content">
            <component
                :is="activityMap[type].component" 
                v-bind="activityMap[type].props(activity)" 
            />
        </div>
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

    console.log(props.activity)

    const type = computed(() => {
        return getFormattedActivityType(props.activity.activity_type);
    });
</script>
<style scoped>
    .activity {
        background-color: var(--surface-100);
        display: flex;
        align-items: center;        
        padding: 12px;
        border: 1px var(--stone-200) solid;
        border-radius: var(--radius-sm);
        transition: all 250ms ease;
        height: min-content;
    }

    .activity:hover {
        border-color: var(--stone-300);
    }

    .activity-content {
        display: flex;
        flex-basis: 90%;
        align-items: center;
        justify-content: space-between;
    }

</style>