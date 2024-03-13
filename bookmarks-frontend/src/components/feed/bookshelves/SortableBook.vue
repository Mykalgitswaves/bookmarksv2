<template>
    
    <label
      for="bs-books"
      :class="['bs-b--book', { 'is-sorting': !isSorted && currentBook, 'sort-target': isSorted }]"
      :disabled="(!isSorted && isLocked)"
      @click="emit('set-sort', id)"
    >
      <div class="sort">{{ order + 1 }}</div>

      <img class="img" :src="imgUrl" alt="" />

      <div class="meta">
        <p class="title">{{ bookTitle }}</p>
        <p class="author">{{ author }}</p>
      </div>

      <input
        v-if="currentBook?.id === id"
        id="bs-books"
        :name="`bs-books-${id}`"
        type="radio"
        :disabled="(!isSorted && isLocked)"
        :value="name"
        :checked="isSorted"
        @click="emit('set-sort', id)"
      />
    </label>

    <button
      v-if="shouldShowSwap()"
      class="swap-btn-target"
      type="button"
      @click="swapWith(nextBook)"
    >
      {{ nextBook?.order }}
    </button>
</template>
<script setup>
import { computed } from 'vue';
import { wsCurrentState } from './bookshelvesRtc';

const props = defineProps({
    order: {
        type: Number,
    },
    id: {
        type: String,
    },
    bookTitle: {
        type: String,
    },
    author: {
        type: String,
    },
    imgUrl: {
        type: String,
    },
    currentBook: {
        type: Object,
    },
    nextBook: {
        type: Object
    },
    prevBook: {
        type: Object
    }
});

const emit = defineEmits(['set-sort']);

const isSorted = computed(() => {
    if(props.currentBook){
        return props.currentBook.id === props.id;
    }
});

function swapWith(book) {
    // Pass in book object so we can don't have to perform finds in next function.
    // However, now we will need to know whether book is going up or down. 
    // If book is going up, then we should take next book + next book

    if(book.order){
        let data = {
            id: props.id,
            target: book,
            order: book.order
        };

        emit('swapped-with', data);
    }
};

function shouldShowSwap() {
    if (!props.currentBook) {
        return false; // If there's no current book, don't show the swap button
    }

    // Hide the one before the current book.
    if(props.currentBook?.order - 1 === props.order){
        return false;;
    }

    if(!props.nextBook){
        return false;
    }

    return (props.currentBook && props.id !== props.currentBook.id) && (props.prevBook?.order !== props.currentBook?.order - 1)
}

const isLocked = computed(() => wsCurrentState.value === 'locked');

</script>
<styles scoped lang="scss">
    .bs-b-book-input {
        border: 1px solid var(--stone-100);
    }

    .bs-b--book {
        position: relative;
        width: 100%;
        display: grid;
        padding: var(--padding-sm);
        border-radius: var(--radius-sm);
        grid-template-columns: 40px 40px auto 40px;
        align-items: center;
        column-gap: 8px;
        transition: all 250ms ease;
        cursor: grab;

        &:hover {
            background-color: var(--stone-100);
        }

        &.sort-target {
            border: 1px solid var(--indigo-500);
            .sort, .img, .meta {
                opacity: 1 !important;
            }
        }

        &.is-sorting {
            grid-template-columns: 40px 40px auto min-content;

            .sort, .img, .meta {
                opacity: .45;
            }
        }

        &.selected-to-swap-target {
            border: 1px solid var(--green-500);
        }

        input:checked {
            fill: var(--indigo-500);
        }
    }   

    @media screen and (max-width: 550px) {
        .bs-b--book {
            padding-left: 0;
            padding-right: 0;
        }
    }

    .swap-btn-target {
        width: min-content;
        border-radius: var(--radius-sm);
        padding: var(--padding-sm);
        background: var(--surface-primary);
        border: 1px solid var(--indigo-500);
        color: var(--indigo-500);
        transform: scale(.8);
        transition: var(--transition-short);

        &:hover, &:focus {
            transform: scale(1);
        }
    }


    .bs-b--book .sort {
        text-align: center;
        font-size: var(--font-lg);
        color: var(--stone-500);
        font-weight: 300;
    }

    .bs-b--book img {
        border-radius: var(--radius-sm);
        justify-self: center;
        width: 100%;
        height: 48px;
        object-fit: cover;
    }

    .bs-b--book .meta {
        padding-left: var(--padding-sm);

        .title { 
            color: var(--stone-800);
            font-size: var(--font-lg);
        }

        .author {
            color: var(--stone-500);
            font-size: var(--font-sm);
        }
    }
</styles>  