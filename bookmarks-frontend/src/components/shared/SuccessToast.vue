<template>
    <div class="toast" v-if="toastType === Toast.defaultType ">
        <button type="button" class="btn btn-small" @click="$emit('dismiss')">
            <IconExit />
        </button>

        <div class="toast-preview">
            <img :src="toast.previewImg" alt="">
            You posted an update for {{ toast.bookTitle }}
        </div>
            
        <a class="toast-link" :href="toast.url">View post here</a>
    </div>

    <!-- Toast for other kind of updates -->
    <div class="toast message" :class="{'deletion': toast.isDeletion }" 
        v-else-if="toastType === Toast.TYPES.MESSAGE_TYPE"
    >
        <button type="button" class="btn btn-small" @click="$emit('dismiss')">
            <IconExit />
        </button>

        <p v-if="toast.message" v-html="toast.message" class="toast-message" />
    </div>
</template>
<script setup>
import IconExit from '../svg/icon-exit.vue'
import { Toast } from './models';

const props = defineProps({
    toastType: {
        type: Boolean,
        required: false,
        default: () => Toast.defaultType,
    },
    toast: {
        type: Object,
        required: true,
    }
});
const emits = defineEmits('dismiss')
</script>
<style scoped>

.toast {
    --block-offset: 110px;

    display: grid;
    position: fixed;
    padding: 10px;
    right: 2vw;
    bottom: var(--block-offset);
    background-color: var(--green-100);
    color: var(--green-600);
    border-radius: var(--radius-sm);
    max-width: 280px;
    min-width: 100px;
    z-index: 1000000;

    &.message {
        display: flex;
        align-items: center;
    }

    &.deletion {
        background-color: var(--red-100);
        color: var(--red-600);
    }
}

.toast-preview {
    height: 45px;
    width: auto;
    aspect-ratio: 1/3;
    border-radius: var(--radius-sm);
}

.toast-message {
    font-size: var(--font-sm);
    max-width: 180px;
}
</style>