<template>
    <div class="
        container mx-auto 
        grid grid-cols-1 
        justify-items-center"
    >
        <h1 class="text-3xl font-semibold text-gray-900 mb-4">Who are some of your<br/> favorite authors?</h1>
        <p class="text-gray-500">Search for some of your favorite authors</p>

        <input
            class="py-2 px-4 rounded-md
            border-2 border-indigo-200 mt-10 w-80 max-w-[600px]" 
            @change="searchBooks($event)"
            placeholder="Search for authors"
            name="searchForAuthor"
            type="text"
        />

        <RouterLink to="/home/1">
            <button class="
                mt-20 px-28 py-3
                bg-indigo-600 rounded-md
                text-indigo-100" 
                type="submit"
            >
            Go to bookshelf
            </button>
        </RouterLink>
    </div>    
</template>

<script>
    export default {

    }
</script>