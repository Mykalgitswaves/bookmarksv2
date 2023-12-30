<template>
    <div>
        Friend ship activities dude.
    </div>
</template>
<script setup>
    import { watchEffect } from 'vue';

    const props = defineProps({
        activity: {
            type: Object,
            required: true
        }
    })
    watchEffect(() => {
        console.log(props, 'Friend Ship friend ship activity')
    })
</script> 