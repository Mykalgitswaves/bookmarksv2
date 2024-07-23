<template>
    <div v-if="postPreviews?.length">
        <div v-for="post in postPreviews" 
            :key="post.id"
            class="preview-post"
        >
            <h3 v-if="post.headline">{{ post.headline }}</h3>
            <h3 v-else> No headline</h3>

            <p>created on {{ post.created_date }}</p>
        </div>
    </div>

    <div v-else class="text-center ml-auto mr-auto mt-5 mb-10">
        <h3 class="text-stone-500 fancy text-xl">No updates <span class="text-2xl">🫥</span></h3>
    </div>
</template>
<script setup>
const props = defineProps({
    postPreviews: {
        type: Array,
        required: true,
    }
});
</script>