<template>
    <div class="bs-b--book" draggable="true" ref="bookRef">
        <div class="sort">
                    {{ book.order }}
        </div>

        <img class="img" :src="book.smallImgUrl" alt="">

        <div class="meta">
            <p class="title">{{ book.title }}</p>
            <p class="author">{{ book.author }}</p>
        </div>
        <IconGrabber data-drag/>
    </div>
</template>
<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { addEventListenersFn, removeEventListenersFn } from './bookshelvesRtc';


const props = defineProps({
    book: {
        type: Object,
        required: true,
    },
});

</script>
<style scoped lang="scss">
    // .bs-b--book {
    //     display: grid;
    //     padding: var(--padding-sm);
    //     border-radius: var(--radius-sm);
    //     grid-template-columns: 40px 40px auto 24px;
    //     align-items: center;
    //     column-gap: 4px;
    //     transition-duration: 200ms;
    //     cursor: grab;

    //     &:hover {
    //         background-color: var(--stone-100);
    //     }
    //     &.dragging {
    //         border-top: 8px solid var(--indigo-600);
    //     }
    //     &.dragged-over {
    //         border: 1px dotted var(--indigo-300);
    //     }
    // }   

    // .bs-b--book .sort {
    //     text-align: center;
    //     font-size: var(--font-lg);
    //     color: var(--stone-500);
    //     font-weight: 300;
    // }

    // .bs-b--book img {
    //     border-radius: var(--radius-sm);
    //     justify-self: center;
    // }
    // .bs-b--book .meta {
    //     padding-left: var(--padding-sm);
    //     .title { color: var(--stone-800); font-size: var(--font-lg)}
    //     .author {
    //         color: var(--stone-500);
    //         font-size: var(--font-sm);
    //     }
    // }
</style>