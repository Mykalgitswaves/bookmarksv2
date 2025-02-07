<template>
    <button 
        type="button" 
        class="btn btn-icon btn-tiny" 
        @click="$emit('close')"
    >
        <IconExit />
    </button>
</template>
<script setup>
import IconExit from '../../svg/icon-exit.vue';

const emits = defineEmits(['close']);
</script>

