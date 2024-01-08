<template>
    <Bookshelves 
        :bookshelves="bookshelves"
        is_admin="true"
    >
        <template v-slot:heading>
            <h1 class="title font-medium">Your bookshelves</h1>
        </template>
        
        <template v-slot:empty-shelf>
            <p>You haven't created any bookshelves yet</p>
        </template>
    </Bookshelves>

    <Bookshelves :bookshelves="[]">
        <template v-slot:heading>
            <h1 class="title font-medium">Liked bookshelves</h1>
        </template>

        <template v-slot:empty-shelf>
            <p>You haven't liked any bookshelves yet</p>
        </template>
    </Bookshelves>
</template>
<script setup>
    import  Bookshelves from './bookshelves.vue'; 

    const bookshelves = [
        {name: 'new', id: 'new', },
        {name: 'new', id: 'new', }
    ]

</script>
<style scoped>




.bookshelf:hover {
    background-color: var(--stone-100);
}

.title {
    font-size: var(--font-2xl);
    color: var(--slate-800);
}
</style>