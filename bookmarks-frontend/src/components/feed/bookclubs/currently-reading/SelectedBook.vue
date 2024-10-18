<template>
    <div class="
        flex flex-row gap-5 py-4 px-4 place-content-start bg-gray-100 rounded-md my-3 
        border-solid border-indigo-200 border-[1px] bg-indigo-50
    ">
        <img class="h-24" :src="book.small_img_url" />
        <div class="flex flex-col justify-center">
        <p class="text-xl font-semibold text-gray-800">{{ book.title }}</p>
        
        <p v-for="name in book.author_names" :key="name" claass="inline text-sm text-gray-800">{{ name }}</p>
        <span class="text-sm text-gray-500">{{ book.publication_year }}</span>
        </div>
    </div>
</template>
<script setup>
defineProps({
    book: {
        type: Object,
        reqiured: true,
    }
});
</script>