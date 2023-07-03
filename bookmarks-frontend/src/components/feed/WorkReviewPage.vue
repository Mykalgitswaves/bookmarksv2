<template>
    
    <div class="flex pt-4">
        <button class="text-indigo-600 underline pr-5" @click="navigateBack">back</button>
        <h2 class="text-2xl font-medium text-slate-600">Kitchen Confidential</h2>
    </div>
    
    <WorkCard 
        :placeholder="placeholder"
        :card="card"
        :user="user"
    />

    <h2 class="text-2xl font-medium text-slate-600">Reviews of this work</h2>
</template>

<script setup>
    import WorkCard from '@/components/feed/WorkCard.vue'
    import { useRouter } from 'vue-router';
    
    const router = useRouter()
    function navigateBack() {
        return router.back()
    }

</script>

<style scoped>


</style>