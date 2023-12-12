<template>
    <button 
        class="btn add-friend-btn"
        :class="buttonMap[currentOptionRef].classes"
        type="button"
        @click="buttonMap[currentOptionRef].db(user, user_profile, currentOptionRef)"
    >
        <span class="flex items-center">
            <component :is="buttonMap[props.currentOption].icon" />
            <span class="ml-2">{{ buttonMap[props.currentOption].text }}</span>
        </span>
    </button>
</template>

<script setup>
    import { computed } from 'vue'
    import { useRoute } from 'vue-router';
    import { buttonMap } from './friendService';

    const props = defineProps({
        currentOption: {
            type: String,
        }
    });

    const currentOptionRef = computed(() => props.currentOption);
    
    const route = useRoute();
    const { user, user_profile } = route.params;
</script>
<style scoped lang="scss">
    @-moz-keyframes spin { 100% { -moz-transform: rotate(360deg); } }
    @-webkit-keyframes spin { 100% { -webkit-transform: rotate(360deg); } }
    @keyframes spin { 100% { -webkit-transform: rotate(360deg); transform:rotate(360deg); } } 
    
    .add-friend-btn {
        display: flex;
        align-items: center;
        justify-self: center;
        color: #fff;
        transition: all 250ms ease; 
    
    &.loading {
        background-color: #525252;
        
        svg {
            -webkit-animation:spin 1s linear infinite;
            -moz-animation:spin 1s linear infinite;
            animation:spin 1s linear infinite;
        }
    }
    
    &.add-friend {
        background-color: #4f46e5;
    }
    
    &.unsend {
        background-color: #3730a3;
    }
    
    &.unfriend {
        background-color: #b91c1c;
    }
}

.add-friend-btn:hover {
    background-color: #3730a3;
}

</style>