<template>
    <button class="text-indigo-600" @click="navigateBack">back</button>
    <div class="text-blue-200">Hello</div>
</template>

<script setup>
    import { useRouter } from 'vue-router';
    
    const router = useRouter()
    function navigateBack() {
        return router.back()
    }

</script>