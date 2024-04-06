<template>
    <section>
        <slot name="heading">
            
        </slot>
        <div 
            class="bookshelves" 
            v-if="bookshelves?.length"
        >
            <div class="bookshelf-container"
                v-for="shelf in bookshelves"
                :key="shelf?.id"
                @click="goToBookshelfPage(user, shelf?.id)"
            >
                <img class="bookshelf" :src="shelf?.book_img_urls[0] || noBookYetUrl" alt=""/>
                
                <p class="bookshelf-title">{{ shelf?.title }}</p>
            </div>
        </div>

        <div class="bookshelves">
            <div class="empty bookshelf">
                <slot name="empty-shelf"></slot>
            </div>
        </div>

        <button 
            v-if="is_admin"
            type="button"
            class="create-bookshelf-btn"
            @click="createNewBookshelf()"
        >
            <IconAddPostVue/>
            create
        </button>
    </section>
</template>
<script setup>
    import { goToBookshelfPage } from '../footernavService';
    import { useRoute, useRouter } from 'vue-router';
    import IconAddPostVue from '../../svg/icon-add-post.vue';
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
        }
    })

    function createNewBookshelf(){
        router.push(`/feed/${user}/bookshelves/create`);
    }

    const noBookYetUrl = 'https://placehold.co/100X150'
</script>
<style scoped>
.bookshelves {
    margin-bottom: var(--margin-md);
    padding: var(--padding-sm);
    display: grid;
    /* grid-template-columns: var(--grid-auto-cols); */
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 10px;
    width: 100%;
}

.bookshelf-container {
    display: grid;
    grid-template-rows: 160px min-content;
    gap: 8px;
}

.bookshelf {
    border-radius: var(--radius-sm);
    border: 1px var(--stone-300) solid;
    padding: var(--padding-sm);
    margin: 5px;
    background-color: var(--stone-50);
    color: var(--stone-600);
    cursor: pointer;
    transition: var(--transition-short);
}

.bookshelf:hover {
    border-color: var(--stone-400);
}

.bookshelf-title {
    padding-top: var(--padding-sm);
    text-align: center;
    font-weight: 400;
    color: var(--stone-800);
}

.bookshelf.empty {
    background-color: var(--primary-surface);
    border: none;
    min-width: 300px;
    text-align: start;
    cursor: auto;
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