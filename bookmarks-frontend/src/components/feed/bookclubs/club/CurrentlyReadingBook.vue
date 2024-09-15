<template>
    <div>
        <p class="text-stone-600 italic">Currently reading</p>

        <div v-if="book" class="currently-reading-book">
            <img :src="book.small_img_url" alt="">

            <div class="book-metadata">
                <h3 class="text-lg text-stone-800">{{ book.title }}</h3>

                <p class="text-sm text-stone-600">
                    {{ helpersCtrl.commanatoredString(book.authorNames) }}
                </p>
            </div>
        </div>

        <div v-else class="currently-reading-book none">
            <h3 class="text-lg text-stone-600">
                This club isn't currently reading anything, 
                <button role="navigation" 
                    type="button" 
                    class="text text-sm text-indigo-600 underline"
                    @click="$emit('currently-reading-settings')"
                >
                    set one now!
                </button>
            </h3>
        </div>
    </div>
</template>
<script setup>
import { helpersCtrl } from '../../../../services/helpers';

defineProps({
    book: {
        type: Object,
    }
})
</script>
<style scoped>
.currently-reading-book {
    /*  */
}
</style>   