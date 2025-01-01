<template>
    <label
        ref="input"
        for="bs-books"
        :class="['bs-b--book', { 
            'is-sorting': !isSorting && currentBook,
            'sort-target': isSorting || isCurrentBookOnOverlay,
            }
        ]"
        :disabled="!unique && (!isSorting && isLocked)"
        @click="showShelfControlsClickHandler"
    >
      <div class="sort">{{ order + 1 }}</div>

      <img class="img" :src="imgUrl" alt="" />

      <div class="meta">
        <p class="title">{{ bookTitle }}</p>
        <p class="author">{{ formatAuthorProps(author) }}</p>
      </div>

      <input
        v-if="currentBook?.id === id"
        id="bs-books"
        :name="`bs-books-${id}`"
        type="radio"
        :disabled="(!isSorting && isLocked)"
        :value="name"
        :checked="isSorting"
        @click="emit('set-sort', props.id)"
      />
    </label>

    <div v-if="unique === Bookshelves.CURRENTLY_READING.prefix && currentlyReadingProgress" class="w-100 mt-2 text-start">
        <div class="progress-toolbar">
            <div class="flex items-center justify-center">
                <button class="badge badge-small badge-purple mt-auto mr-2"
                    type="button"
                    @click="showProgressBar = !showProgressBar"
                >
                    {{ currentlyReadingProgress.progress + ' / ' + currentlyReadingProgress.remaining }}
                </button>

                <InlineTooltip alignment="left" color="purple">
                    <template #message>
                        Click on the pages to view your progress on this book
                    </template>
                </InlineTooltip>
            </div>

            <div class="flex gap-2">
                <button type="button" 
                    class="btn btn-icon btn-tiny icon text-stone-400 btn-ghost text-xs fancy" 
                    @click="emit('editing-current-book-note', book )"
                >
                    <IconNote />
                    
                    <span v-if="!noteForShelf">Add note</span>

                    <span v-else>Edit note</span>
                </button>

                <button class="btn btn-ghost btn-tiny text-xs text-stone-400 fancy" type="button" @click="$emit('update-currently-reading-book', book)">
                    update progress
                </button>    
            </div>
        </div>

        <KeepAlive>
            <Transition name="content">
                <BookProgressBar 
                    v-if="showProgressBar" 
                    :book="book" 
                    :current-page="currentlyReadingProgress.progress" 
                    :total-pages="currentlyReadingProgress.remaining"
                />
            </Transition>
        </KeepAlive>
    </div>
    <div class="w-100" v-else>
        <button type="button" 
            class="btn btn-icon btn-tiny icon text-stone-400 btn-ghost text-xs fancy ml-auto" 
            @click="emit('editing-current-book-note', book )"
        >
            <IconNote />
            
            <span v-if="!noteForShelf">Add note</span>

            <span v-else>Edit note</span>
        </button>
    </div>
        
    <p v-if="noteForShelf" class="text-stone-500 weight-300 mr-auto max-w-[768px]">
        {{ truncateText(noteForShelf, 150) }}
    </p>

    <button
      v-if="shouldShowSwap()"
      class="swap-btn-target"
      type="button"
      @click="swapWith(index)"
    >
      {{ currentBook?.order > order ? order + 2 : order + 1  }}
    </button>
    
    <!-- <button v-if="shouldShowBookToolbar"
        type="button"
        class="btn btn-tiny text-sm icon btn-remove ml-auto"
        @click="$emit('removed-book', props.id)"
    >
        <IconDelete />

        Remove from shelf
    </button> -->
</template>
<script setup>
import { computed, ref } from 'vue';
import { wsCurrentState } from './bookshelvesRtc';
import { truncateText } from '../../../services/helpers';
import { Bookshelves } from '../../../models/bookshelves';
import IconDelete from '../../svg/icon-trash.vue';
import BookProgressBar from './BookProgressBar.vue';
import InlineTooltip from '../../shared/InlineTooltip.vue';
import IconNote from '../../svg/icon-note.vue';

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
    book: {
        type: Object,
        required: true,
    },
    currentBook: {
        type: Object,
    },
    nextBook: {
        type: Object
    },
    prevBook: {
        type: Object
    },
    index: {
        type: Number
    },
    isEditing: {
        type: Boolean
    },
    noteForShelf: {
        type: String
    },
    unique: {
        type: String,
    },
    currentBookForOverlay: {
        type: Object
    }
});

const input = ref('input');
const emit = defineEmits(['set-sort', 'show-book-controls-overlay', 'swapped-with', 'update-currently-reading-book']);

const isSorting = computed(() => {
    if(props.currentBook){
        return props.currentBook.id === props.id;
    }
});

const isCurrentBookOnOverlay = computed(() => {
    return !!(props.currentBookForOverlay?.id === props.id)
})

function swapWith(index) {
    // Pass in an index of the book you want to swap with!
    
    let data = {
        id: props.id,
        target_index: index,
    };
    
    emit('swapped-with', data);
    input.value.scrollIntoView({ behavior: 'smooth', block: 'center' });
};


function formatAuthorProps(authorData){
    if (authorData && Array.isArray(authorData) && authorData.length) {
        return authorData[0];
    }
    return '';
}

// Show shelf controls for each book while not editing the shelves.
function showShelfControlsClickHandler(){
    if(!props.isEditing){
        let payload = {};

        payload[props.unique] = props.id;
        emit('show-book-controls-overlay', payload);
    }
    emit('set-sort', props.id);
}

function shouldShowSwap() {
    if (!props.currentBook) {
        return false; // If there's no current book, don't show the swap button
    }

    // // We dont want to show swap buttons for editing books.
    // if(props.isEditing){
    //     return false;
    // }

    if (props.currentBookForOverlay) {
        return false;
    }

    // Hide the one before the current book.
    if(props.currentBook?.order - 1 === props.order){
        return false;;
    }

    // because its the end of the list we handle that case outside of this component.
    if(!props.nextBook){
        return false;
    }

    // Show the swap button if the current book is not the same as the book we're looking at
    return !!(props.id !== props.currentBook.id)
}

const shouldShowBookToolbar = computed(() => {
    if(!props.currentBook) return false;

    if(props.currentBook.id === props.id && props.isEditing){
        return true;
    }
});

const isLocked = computed(() => wsCurrentState.value === 'locked');

/**
 * @description computed props for progress bars on currently reading shelf
 */
const currentlyReadingProgress = computed(() => {
    if (props.unique === Bookshelves.CURRENTLY_READING.prefix) {
        return { 
            progress: props.book.current_page ||= 0,
            remaining: props.book.total_pages ||= 0,
        }
    } 
    return false;
});

/**
 * currently reading bookshelf functions
 * For shit related to SortableBook components in the context of a currently reading shelf
 */

const showProgressBar = ref(false);

/**
 * End currently reading shelf functions
 */

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

    .remove-btn-button {
        display: flex;
        justify-content: start;
        align-items: start;
        margin-left: auto;
        margin-right: var(--margin-sm);
        color: var(--stone-600);
        transition: var(--transition-short);
    }

    .remove-btn-button:hover {
        color: var(--red-500);
        text-decoration: underline;
    }

    .progress-toolbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
</styles>  