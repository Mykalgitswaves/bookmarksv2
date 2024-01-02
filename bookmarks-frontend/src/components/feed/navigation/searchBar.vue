<template>
    <div class="container flex items-center space-between">
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
        <div class="btn-relative">
            <button
                class="btn"
                type="button"
                @click="isShowingFilters = !isShowingFilters"
            >
                <IconMenu/>
            </button>

            <div v-if="isShowingFilters" class="popout-flyout filter">
                <SearchFilters 
                :active-filter-mapping="activeFilterMapping"
                @current-filter="($event) => currentFilter = $event"
                />
            </div>
        </div>
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
    "reset": false,
});

// defaults to none.
const currentFilter = ref('');

// manually loop through each key in ref and turn to false.

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
        })
    }
    activeFilterMapping[newValue] = !activeFilterMapping[newValue];
    console.log(activeFilterMapping)
    emit('toggle-filter', activeFilterMapping);
});


// Gets own specific search Request from here.
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

const debouncedSearchRequest = debounce(searchRequest, 500, false)
</script>

<style scoped>

.hidden { display: none; visibility: hidden; }
.searchbar {
    color: #5A67D8;
    font-weight: 400;
}

.searchbar input {
    max-width: 300px;
    min-width: 280px;
    width: 100%;
}

.filter-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    justify-content: space-between;
    max-width: 400px;
}
</style>