<template>
    <div class="searchbar-wrapper">
        <div class="searchbar">
                <label for="searchbar"><span class="hidden">Search</span>
                    <input
                        name="searchbar"
                        v-model="searchData"
                        @keyup="debouncedSearchRequest($event)"
                        class="border-solid border-2
                        border-indigo-300 py-2 pl-2 rounded-md" 
                        type="text" placeholder=" What are you looking for?"
                    />
                </label>
        </div>

        <TransitionGroup name="content" tag="div" class="filter-container">
            <button
                class="menu-btn"
                type="button"
                @click="isShowingFilters = !isShowingFilters"
            >
                <IconMenu/>
            </button>
            
            <SearchFilters
                    v-if="!isShowingFilters"
                    class="filter-grid text-sm" 
                    :active-filter-mapping="activeFilterMapping"
                    @current-filter="($event) => currentFilter = $event"
            />
        </TransitionGroup>
    </div>
</template>
<script setup>
import { ref, watch, reactive } from 'vue';
import { searchResultStore } from '@/stores/searchBar.js'; 
import { helpersCtrl } from '../../../services/helpers';
const { debounce } = helpersCtrl;
import IconMenu from '../../svg/icon-hmenu.vue';
import SearchFilters from './searchfilters.vue';

const responseBlob = ref(null);
const isShowingFilters = ref(false);
const searchData = ref('');
const store = searchResultStore();

const emit = defineEmits(['store-updated']);

const activeFilterMapping = reactive({
    "authors": true,
    "users": true,
    "books": true,
    "genres": true,
    "books_by_author": true,
    "reset": false,
});

// defaults to none.
const currentFilter = ref('');

watch(currentFilter, (newValue) => {
    if(newValue === 'reset') {
        Object.keys(activeFilterMapping).forEach((key) => {
            if(key !== "reset"){
                activeFilterMapping[key] = true
            } else {
                // Set reset back to false then break
                activeFilterMapping[key] = false;
                return;
            }
        });
    }

    activeFilterMapping[newValue] = !activeFilterMapping[newValue];
    emit('toggle-filter', activeFilterMapping);
});


// Gets own specific search Request from here so we can debounce it?.
async function searchRequest() {
    if (searchData.value.length > 1) {
        try {
            return await fetch(`http://127.0.0.1:8000/api/search/${searchData.value}`) 
                .then((data) => data.json())
                .then(res => {
                    responseBlob.value = res.data;
                    store.saveAndLoadSearchResults(res.data);
                    emit('store-updated', store.data);
                });
        } catch(err) {
                return console.error(err);
        }
}}
// Might want to do something else idk.
const debouncedSearchRequest = debounce(searchRequest, 500, false)
</script>
<style scoped>

.hidden { display: none; visibility: hidden; }

.searchbar-wrapper {
    container-type: inline-size;
    display: flex;
    justify-content: space-between;
    width: 100%;
    flex-wrap: wrap;
}

@media (min-width: 850px) {
    .searchbar-wrapper {
        max-width: 850px;
    }
}

/* Mobile media query */
@media screen and (max-width: 768px) {
    .searchbar-wrapper {
        flex-direction: column;
        align-items: start;
    }
}

.searchbar {
    color: #5A67D8;
    font-weight: 400;
}

.searchbar input {
    max-width: 300px;
    min-width: 280px;
    width: 100%;
}

@container (max-width: 746px) {
    .searchbar input {
        width: calc(100vw - 20px);
    }
}

.filter-container {
    display: flex;
}

@container (max-width: 746px) {
    .filter-container {
        margin-top: var(--margin-md);
    }   
}

.menu-btn {
    padding: var(--btn-padding-base);
    margin-right: var(--margin-md);
}

.filter-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    justify-content: space-between;
    align-items: center;
    max-width: 400px;
}

</style>