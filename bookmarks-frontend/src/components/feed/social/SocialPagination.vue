<template>
    <div>
      <div class="pagination">
            <button
                type="button"
                class="btn"
                :class="{ disabled: currentPage + 1 > totalPages}"
                :disabled="currentPage + 1 > totalPages"
                @click="goToPage(currentPage + 1)"
            >
                View more
            </button>
        </div>
    </div>
  </template>
  
<script setup>
import { ref } from 'vue';

const props = defineProps({  
    currentPage: {
        type: Number,
        required: true,
    },
    totalPages: {
        type: Number,
        required: true,
    }
});

const emit = defineEmits(['page-changed'])
const currentPage = ref(props.currentPage);
const totalPages = ref(props.totalPages);

const goToPage = (page) => {
    currentPage.value = page;
    // You can emit an event or perform any action here when a page is clicked
    emit('page-changed', currentPage.value);
};
</script>
<style scoped>
    .pagination {
        display: grid;
        margin-top: 14px;
        color: #4f46e5;
        font-size: 18px;
        justify-content: center;
    }

    .pagination button {
            transition: all 250ms ease;
        }

    .pagination button:hover:not([disabled]) {
        background-color: #e0e7ff;
    }
    .pagination .disabled {
        color: #a8a29e;
    }
</style>