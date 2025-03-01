<template>
    <div class="
        flex flex-row gap-5 py-4 px-4 place-content-start bg-gray-100 rounded-md my-3 
        border-solid border-[1px]" 
        :class="{
            'border-indigo-200 bg-indigo-50': !setBook, 
            'bg-yellow-100': book?.isFinishedReading,
        }"
    >
        <img class="h-24" :src="book.small_img_url" />
        <div class="flex flex-col justify-center">
        <p class="text-xl font-semibold text-gray-800">{{ book.title }}</p>
        
        <p v-for="name in book.author_names" :key="name" claass="inline text-sm text-gray-800">{{ name }}</p>
        
        <span class="text-sm text-gray-500">{{ book.publication_year }}</span>
        </div>
    </div>

    <p v-if="setBook && book?.isFinishedReading" 
        class="fancy text-stone-500"
    >Finished reading 🎉</p>
</template>
<script setup>
const props = defineProps({
    book: {
        type: Object,
        required: true,
    },
    setBook: {
        type: Boolean,
        required: false,
    }
});
</script>