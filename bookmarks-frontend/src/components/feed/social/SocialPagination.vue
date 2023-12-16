<template>
    <div>
      <div class="pagination">
            <button
                type="button"
                class="btn"
                :class="{ disabled: currentPage - 1 < 0}"
                :disabled="currentPage - 1 < 0" 
                @click="goToPage(currentPage - 1)"
            >
                Previous
            </button>

            <button
                type="button"
                class="btn"
                :class="{ disabled: currentPage + 1 >= totalPages}"
                :disabled="currentPage + 1 >= totalPages"
                @click="goToPage(currentPage + 1)"
            >
                Next
            </button>
        </div>
    </div>
  </template>
  
<script setup>
import { ref, computed } from 'vue';

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
<style scoped lang="scss">
    .pagination {
        margin-top: 14px;
        display: flex;
        justify-content: center;
        column-gap: 18px;
        color: #4f46e5;
        font-size: 18px;

        .disabled {
            color: #a8a29e;
        }
    }
</style>