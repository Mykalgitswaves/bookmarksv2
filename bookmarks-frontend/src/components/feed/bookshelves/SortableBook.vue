<template>
    <button 
        v-if="sortTarget && order % 2 == 1"
        class="swap-btn-target"
        type="button"
        @click="swapWith(-1)"
    >
        <IconHitTarget />
    </button>

    <label
        for="bs-books"
        class="bs-b--book" 
        :class="{
            'is-sorting': (!isSorted && sortTarget), 
            'sort-target': isSorted,        
        }"
        @click="emit('set-sort', id)"
    >
        <div class="sort">
            {{ order + 1 }}
        </div>

        <img class="img" :src="imgUrl" alt="">

        <div class="meta">
            <p class="title">{{ bookTitle }}</p>
            <p class="author">{{ author }}</p>
        </div>

        <input
            v-if="sortTarget?.id === id"
            id="bs-books" 
            :name="`bs-books-${id}`"
            type="radio"
            :value="name"
            @click="emit('set-sort', id)"
        />
    </label>

    <button 
        v-if="sortTarget && order % 2 == 1"
        class="swap-btn-target"
        type="button"
        @click="swapWith(1)"
    >
        <IconHitTarget class="one-80-deg"/>
    </button>

</template>
<script setup>
import { computed } from 'vue';
import IconHitTarget from '../../svg/icon-hit-target.vue';

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
    sortTarget: {
        type: Object,
    },
});

const emit = defineEmits(['set-sort']);

const isSorted = computed(() => {
    return !!props.sortTarget?.id === props.id;
});

function swapWith(num){   
    let data = {
        id: props.id,
        order: props.order + num,
    };

    emit('swapped-with', data);
}

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
        }

        &.is-sorting:not(&.sort-target) {
            grid-template-columns: 40px 40px auto min-content;
            .sort, .img, .meta {
                opacity: .45;
            }
        }

        &.selected-to-swap-target {
            border: 1px solid var(--green-500);
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