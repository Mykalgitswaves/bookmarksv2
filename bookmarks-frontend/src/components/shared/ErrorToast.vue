<template>
    <div class="toast" ref="toast">
        {{ message }}

        <button 
            v-if="refresh"
            class="refresh"
            type="button"
            @click="forceRefresh"
        >
            Refresh
        </button>
    </div>
</template>
<script setup>
import { ref } from 'vue';

const props = defineProps({
    message: {
        type: String,
        required: true,
    },
    refresh: {
        type: Boolean,
        required: false,
        default: false,
    }
});

function forceRefresh(){
    document.location.reload();
}

</script>
<style scoped>

.toast {
    --block-offset: 110px;

    display: grid;
    position: fixed;
    padding: 10px;
    right: 2vw;
    bottom: var(--block-offset);
    background-color: var(--red-100);
    color: var(--red-600);
    border-radius: var(--radius-sm);
    max-width: 280px;
    min-width: 100px;
    z-index: 1000000;

    .refresh {
        justify-self: end;
        text-align: end;
        color: var(--red-800);
        font-weight: 500;
    }
}

</style>