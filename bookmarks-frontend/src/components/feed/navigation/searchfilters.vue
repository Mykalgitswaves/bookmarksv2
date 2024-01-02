<template>
    <div :class="$attrs.class">
        <button
            class="filter"
            :class="activeFilterMapping['reset'] ? 'active' : 'inactive'"
            type="button"
            name="resetFilters"
            @click="emit('current-filter', 'reset')"
        >
            Reset
        </button>

        <button 
            class="filter"
            :class="activeFilterMapping['authors'] ? 'active' : 'inactive'"
            type="button"
            name="authorsFilter"
            @click="emit('current-filter', 'authors')"
        >
            Authors
        </button>

        <button 
            class="filter"
            :class="activeFilterMapping['books'] ? 'active' : 'inactive'"
            type="button"
            name="booksFilters"
            @click="emit('current-filter', 'books')"
        >
            Books
        </button>

        <button 
            class="filter"
            :class="activeFilterMapping['users'] ? 'active' : 'inactive'"
            type="button"
            name="usersFilters"
            @click="emit('current-filter', 'users')"
        >
            Users
        </button>    

        <button 
            class="filter"
            :class="activeFilterMapping['books_by_author'] ? 'active' : 'inactive'"
            type="button"
            name="usersFilters"
            @click="emit('current-filter', 'books_by_author')"
        >
            Books by author
        </button>    
    </div>
</template>
<script setup>
    const emit = defineEmits(['current-filter']);
    const props = defineProps({
        activeFilterMapping: {
            type: Object
        }
    });
</script>
<style scoped>
button {
    text-align: center;
    transition: var(--transition-short);
    border-radius: var(--radius-sm);
    padding: var(--btn-padding-base);
    max-height: 40px;
}

.active {
    color: #1e1b4b;
    background-color: #e0e7ff;
}

.inactive {
    background-color: #c7d2fe;
    color: #1e1b4b;
}
</style>