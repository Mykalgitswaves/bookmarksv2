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
            <div class="bookshelf"></div>
            <p class="bookshelf-title">{{ shelf?.name }}</p>
        </div>
        </div>

        <div v-else class="bookshelves">
            <div class="empty bookshelf">
                <slot name="empty-shelf"></slot>
            </div>
        </div>

        <button 
            v-if="is_admin"
            type="button"
            class="create-bookshelf-btn"
            @click=""
        >
            <IconAddPostVue/>
            create
        </button>
    </section>
</template>
<script setup>
    import { goToBookshelfPage } from '../footernavService';
    import { useRoute } from 'vue-router';
    import IconAddPostVue from '../../svg/icon-add-post.vue';
    const route = useRoute();
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
</script>
<style scoped>
.bookshelves {
    border: 2px  var(--indigo-200) solid;
    border-radius: var(--radius-md);
    margin-top: 20px;
    margin-bottom: var(--margin-md);
    padding: var(--padding-sm);
    display: grid;
    /* grid-template-columns: var(--grid-auto-cols); */
    grid-template-columns: repeat(auto-fit,  120px);
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
    text-align: center;
    color: var(--stone-800);
    font-weight: 400;
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