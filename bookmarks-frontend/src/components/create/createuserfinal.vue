<template>
    <div class="container mx-auto">
        <h1 class="text-3xl font-semibold text-gray-900 mb-4">Who are some of your favorite authors?</h1>
        <p class="text-gray-500">Search for some of your favorite authors</p>

        <input
            class="w-[80vw] max-w-[650px] py-2 px-4 rounded-md
            border-2 border-indigo-200 mt-20" 
            @change="searchBooks($event)"
            placeholder="Search for authors"
            name="searchForAuthor"
            type="text"
        />
    </div>    
</template>

<script>

    export default {

    }
</script>