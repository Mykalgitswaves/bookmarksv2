<template>
    <div class="mt-10">
        <h1 class="title font-medium">Your bookshelves</h1>
        
        <div 
            class="bookshelves" 
            v-if="bookshelves?.length"
        >
            <div
                class="bookshelf"
                v-for="shelf in bookshelves"
                :key="shelf?.id"
                @click="goToBookshelfPage(user, shelf?.id)"
            >
                {{ shelf?.name }}
            </div>
        </div>
        <div v-else class="bookshelves">
            <div class="bookshelf">
                <span class="fancy text-md">Nunca</span>
            </div>
        </div>
    </div>
    
    <div class="mt-10">
        <h1 class="title font-medium">Liked bookshelves</h1>
        
        <div class="bookshelves">
            <div class="bookshelf">
                <span class="fancy text-md">Nunca</span>
            </div>
        </div>
        <p>you haven't liked any bookshelves yet, find some here!</p>   
    </div>
</template>
<script setup>
    import { goToBookshelfPage } from '../footernavService';
    import { useRoute } from 'vue-router';
    const route = useRoute();
    const { user } = route.params;
    const bookshelves = [
        {name: 'new', id: 'new', },
        {name: 'new', id: 'new', }
    ]

</script>
<style scoped>
.bookshelves {
    border: 2px  var(--indigo-200) solid;
    border-radius: var(--radius-md);
    margin-top: 20px;
    margin-bottom: 40px;
    padding: var(--padding-md);
    display: grid;
    /* grid-template-columns: var(--grid-auto-cols); */
    grid-template-columns: repeat(auto-fit,  120px);
    gap: 10px;
    width: 100%;
}

.bookshelf {
    text-align: center;
    border-radius: var(--radius-sm);
    border: 1px var(--stone-300) solid;
    padding: var(--padding-sm);
    margin: var(--margin-shim-sm);
    background-color: var(--stone-50);
    color: var(--stone-600);
    cursor: pointer;
    transition: var(--transition-short);
}

.bookshelf:hover {
    background-color: var(--stone-100);
}

.title {
    font-size: var(--font-2xl);
    color: var(--slate-800);
}
</style>