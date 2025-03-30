<template>
    <div class="
        flex flex-row gap-5 py-4 px-4 place-content-start rounded-md my-3 
        border-solid border-[1px] relative" 
        :class="{
            'border-indigo-200 bg-indigo-50': !setBook, 
            'bg-yellow-100': book?.isFinishedReading,
            'finished-reading': (
                finished?.user || finished?.club
            ),
        }"
    >
        <img class="h-24" :src="book.small_img_url" />

        <div class="flex flex-col justify-center">
            <p class="text-xl font-semibold text-gray-800">{{ book.title }}</p>
            
            <p v-for="name in book.author_names" :key="name" claass="inline text-sm text-gray-800">{{ name }}</p>
            
            <span class="text-sm text-gray-500">{{ book.publication_year }}</span>
        </div>

        <span v-if="finished?.user || finished?.club" 
            class="finished-reading-blurb text-sm fancy text-stone-700 flex gap-2 items-center"
        >
            {{
                finished.club ? 'The club finished this book' : 'You finished this book'
            }}
            <IconCrown />
        </span>
    </div>

    <p v-if="setBook && book?.isFinishedReading" 
        class="fancy text-stone-500"
    >Finished reading 🎉</p>
</template>
<script setup lang="ts">
import { PropType } from 'vue';
import IconCrown from '@/components/svg/icon-crown.vue'

defineProps({
    book: {
        type: Object,
        required: true,
    },
    setBook: {
        type: Boolean,
        required: false,
    },
    // Used for gauging whether members of a book club are finished reading yet. 
    finished: {
        type: Object as PropType<{
            club: Boolean,
            user: Boolean,
        }>,
        required: false,
    },
});

</script>
<style scoped>
.finished-reading {
    background-color: var(--yellow-300) !important;
}

.finished-reading-blurb {
    position: absolute;
    bottom: 5px;
    right: 10px;
}
</style>