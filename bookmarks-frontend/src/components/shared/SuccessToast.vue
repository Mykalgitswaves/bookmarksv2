<template>
    <div class="toast">
        <button type="button" class="btn btn-small" @click="emit('dismiss')">
            <IconExit />
        </button>

        <div class="toast-preview">
            <img :src="toast.previewImg" alt="">
            You posted an update for {{ toast.bookTitle }}
        </div>
            
        <a class="toast-link" :href="toast.url">View post here</a>
    </div>
</template>
<script setup>
import IconExit from '../svg/icon-exit.vue'

const props = defineProps({
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
}

</style>