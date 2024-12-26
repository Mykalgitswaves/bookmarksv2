<template>
    <section class="bookshelves-section">
        <slot name="heading">
            
        </slot>
        <!-- <TransitionGroup name="content" tag="div"> -->
        
        <div class="bookshelves" 
            v-if="bookshelves?.length"
        >
            <!-- the actual clickable shelves. -->
            <div class="bookshelf-container"
                v-for="shelf in isPreview(bookshelves)"
                :key="shelf?.id"
                @click="goToBookshelfPage(user, shelf?.id)"
            >
                <img class="bookshelf" :src=getImgUrl(shelf) alt=""/>

                <div>
                    <h4 class="bookshelf-title">{{ shelf?.title }}</h4>

                    <p class="bookshelf-description">{{ truncateText(shelf?.description, 100) }}</p>
                </div>
                
                <div class="ml-auto mr-2 text-sm fancy">
                    <span :class="{'text-indigo-500': shelf.books?.length > 0 || shelf.books_count > 0}">{{ shelf?.books?.length || shelf?.books_count || 0}} books</span>
                </div>
            </div>
        </div>

        <!-- loading indicatorrrr -->
        <div :aria-busy="!!props.dataLoaded" class="bookshelves loading"> 
            <div v-if="!props.dataLoaded" class="bookshelf-container gradient" >
                <div class="bookshelf gradient"></div>

                <div>
                    <h4 class="bookshelf-title">loading...</h4>

                    <p class="bookshelf-description">patience is a virtue</p>
                </div>
            </div>
        </div>
    <!-- </TransitionGroup> -->
    <!-- Finished loading indicator -->

        <div v-if="dataLoaded && !bookshelves.length">
            <div class="empty bookshelf">
                <slot name="empty-shelf"></slot>
            </div>
        </div>
        
        <div class="flex gap-2 items-center mt-5" v-if="!isUnique">
            <button v-if="is_admin"
                type="button"
                class="create-bookshelf-btn btn-tiny text-sm"
                @click="createNewBookshelf()"
            >
                Create
            </button>

            <button v-if="!isOnSectionPage && bookshelves?.length > 3" 
                type="button" 
                class="create-bookshelf-btn btn-tiny text-sm"
                @click="router.push(viewBookshelvesForSection(user, 'created_bookshelves'))"
            >
                View all created bookshelves
            </button>
        </div>
    </section>
</template>
<script setup>
    import { goToBookshelfPage } from '../footernavService';
    import { useRoute, useRouter } from 'vue-router';
    import { truncateText } from '../../../services/helpers';
    import { viewBookshelvesForSection } from './bookshelvesRtc';
    const route = useRoute();
    const router = useRouter();
    const { user } = route.params;

    const props = defineProps({
        bookshelves: {
            type: Array,
            required: false,
        },
        is_admin: {
            type: Boolean,
            required: true
        },
        dataLoaded: {
            type: Boolean,
            default: false,
        },
        isOnSectionPage: {
            type: Boolean,
        },
        sectionId: {
            type: String,
            required: false,
        },
        isUnique: {
            type: String,
            required: false,
        },
    })

    function createNewBookshelf(){
        router.push(`/feed/${user}/bookshelves/create`);
    }

    const noBookYetUrl = 'https://placehold.co/45X45';

    // 
    function isPreview(bookshelves){
        if(props.isPreview){
            // Three shelves
            return bookshelves.slice(0,3);
        }
        return bookshelves;
    }

    function getImgUrl(bookshelf){
        // If book_img_urls is not an array, check for books[0].small_img_url
        // If that is not available, return a placeholder image
        if (bookshelf?.book_img_urls && bookshelf?.book_img_urls[0]) {
            return bookshelf?.book_img_urls[0];
        } else if (bookshelf?.books && bookshelf?.books[0]?.small_img_url) {
            return bookshelf?.books[0]?.small_img_url;
        } else {
            return noBookYetUrl;
        }
    }
</script>
<style scoped lang="scss">

.bookshelves-section {
    min-height: 63px;
}

.bookshelves {
    display: flex;
    flex-direction: column;
    row-gap: 10px;
    width: 100%;

    &.loading {
        margin-bottom: 0;
    }

    &.loading:not(:has(:first-child)){
        padding-top: 0;
        padding-bottom: 0;
    }
}

.bookshelf-container {
    --x-axist-offset: 20px;

    @media screen and (max-width: 550px) {
        --x-axis-offset: 4px;
    }

    display: flex;
    align-items: center;
    column-gap: 8px;
    max-width: 880px;
    width: 100%;
    padding-left: var(--x-axist-offset);
    padding-top: 4px;
    padding-bottom: 4px;
    border-radius: var(--radius-sm);
    margin-right: auto;
    border: 1px var(--stone-100) solid;
    transition: all 150ms ease-in;
}

.bookshelf-container:hover {
    background-color: var(--stone-100);
    border: 1px solid var(--indigo-300);
}

.bookshelf {
    height: 45px;
    width: 45px;
    padding: 4px;
    color: var(--stone-600);
    cursor: pointer;
    transition: var(--transition-short);
    object-fit: cover;
}

.bookshelf:hover {
    border-color: var(--stone-400);
}

.bookshelf-title {
    font-family: var(--fancy-script);
    font-size: var(--font-xl);
    font-weight: 400;
    color: var(--stone-800);
    word-break: anywhere;
}

.bookshelf-description {
    font-size: var(--font-sm);
    color: var(--stone-500);
}

.bookshelf.empty {
    background-color: var(--primary-surface);
    border: none;
    min-width: 300px;
    text-align: start;
    cursor: auto;
    padding-left: 0;
}

.create-bookshelf-btn {
    display: flex;
    column-gap: 4px;
    background-color: var(--indigo-500);
    color: var(--gray-50);
    padding: 8px var(--padding-sm);
    border-radius: var(--radius-sm);
    margin-bottom: var(--margin-sm);
    transition: var(--transition-short);
}

.create-bookshelf-btn:hover {
    background-color: var(--indigo-600);
}
</style>