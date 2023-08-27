<template>
    <div class="nav-button-group searchbar">
        <button 
            class="footer-nav-button" 
            type="button"
            @click="toggleSearchBar"
        >
            <IconSearch/>
        </button>
        <div v-show="!isSearchActive">
            <p class="ml-2">Search</p>
            <input 
                v-model="searchData"
                @keydown="searchRequest(searchData)"
                class="w-100 border-solid border-2
                border-indigo-300 py-2 mx-2 pl-2 rounded-md" 
                type="text" placeholder=" Search"
            />
        </div>
    </div>
</template>
<script setup>
    import { ref } from 'vue';
    import { searchResultStore } from '@/stores/searchBar.js';
    import IconSearch from '@/components/svg/icon-search.vue';

    let isSearchActive = ref(Boolean);
    function toggleSearchBar() {
        isSearchActive.value = !isSearchActive.value
        const toggleSearchBarEvent = new Event('toggleSearchBar', {
            detail: isSearchActive.value,
            bubbles: true, 
            composed: true
        });
        
        window.dispatchEvent(toggleSearchBarEvent);
    }

    const responseBlob = ref(null);
    const searchData = ref('');
    const store = searchResultStore();

    async function searchRequest(searchData) {
        if (searchData.length > 1) {
            try {
                return await fetch(`http://127.0.0.1:8000/api/search/${searchData}`) 
                    .then((data) => data.json())
                    .then(res => {
                        responseBlob.value = res.data;
                        store.saveAndLoadSearchResults(res.data);
                        console.log(store.data);
                    });
            } catch(err) {
                    return console.error(err);
            }
    }}
</script>

<style scoped>
.searchbar {
    display: flex;
    flex-direction: row;
    justify-content: space-around;
    color: #5A67D8;
    font-weight: 500;
}

.nav-button-group {
    display: flex;
    flex-direction: row;
    justify-items: center;
    align-items: center;
    gap: .25rem;
    cursor: pointer;
    color: #5A67D8;
    font-weight: 500;
    padding: .4rem .25rem ;
    border-radius: .5rem;
}

@media only screen and (min-width: 768px) {
    footer {
        position: sticky;
        top: calc(30vh);
        width: 100%;
        max-width: 240px;
        height: calc(100% - 274px);
        display: flex;
        flex-direction: column;
        justify-content: start;
        gap: 1.5rem;
        align-items: center;
        background: transparent
    }

    .nav-button-group {
        position: sticky;
        top: 3rem;
        display: flex;
        align-self: start;
        width: 100%;
        border-radius: .5rem;
        padding-block: .5rem;
    }

    /* #Todo: Make the search bar responsive so it looks better on mobile and desktop */
    .searchbar {
        display: flex;
        flex-direction: row;
    }
}
.footer-nav-button {
    border-radius: 50%;
    padding: .5rem;
    margin-left: 1rem;
    margin-right: 1rem;
    color: #667EEA;
    border: solid 2px #667EEA;
    align-content: center;
    justify-content: center;
    transition-duration: 250ms;
}
.footer-nav-button:hover {
    border: solid 2px #343fa9;
    color: #343fa9;
    transform: scale(1.02);
}
</style>