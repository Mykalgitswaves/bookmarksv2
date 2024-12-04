<template>
    <div class="searchbar">
        <label for="searchbar-input">
            <input 
                id="searchbar-input"
                :class="{'has-value': !!search_params.length}"
                class="searchbar-input" 
                type="text" 
                v-model="search_params"
                @keyup="debouncedSearchRequest($event)"
            >
        </label>

        <div class="searchbar-icon">
            <IconSearch />
        </div>
    </div>
</template>
<script setup>
import { ref } from 'vue';
import { urls } from '../../../services/urls';
import { db } from '../../../services/db';
import { helpersCtrl } from '../../../services/helpers';
import { PubSub } from '../../../services/pubsub';
import IconSearch from '@/components/svg/icon-search.vue';

const { debounce } = helpersCtrl;
const search_params = ref('');
const responseBlob = ref(null);

function searchRequest() {
    if (search_params.value.length > 1) {
        // Define your URLs and feature keys
        const searchFeatures = {
            general_search: urls.search.general(search_params.value), // This feature outputs an object
            bookClubs: urls.search.bookClub(search_params.value), // Outputs an array
            bookshelves: urls.search.bookshelf(search_params.value), // Outputs an array
            // Add more features as needed
        };

        // Map the feature keys to db.get calls
        const requests = Object.entries(searchFeatures).map(([key, url]) =>
            db.get(url, null, false)
                .then((res) => {
                    if (key === 'general_search') {
                        // Handle the feature that outputs an object
                        return res.data; // Directly return the object keys at the top level
                    } else {
                        // Wrap arrays in a feature-specific key
                        return { [key]: res.data };
                    }
                })
                .catch((err) => {
                    return key === 'general_search' ? {} : { [key]: null }; // Return empty object or null
                })
        );

        // Use Promise.all to execute all requests concurrently
        Promise.all(requests).then((responses) => {
            // Merge all responses into a single object
            responseBlob.value = responses.reduce((acc, response) => {
                if (typeof response === 'object' && !Array.isArray(response)) {
                    // Merge top-level object keys
                    return { ...acc, ...response };
                }
                // Merge other feature-specific keys
                return { ...acc, ...response };
            }, {});
            console.log(responseBlob.value);
            // Publish combined data to PubSub or process further
            PubSub.publish('nav-search-get-data', responseBlob.value);
        });
    }
}

const debouncedSearchRequest = debounce(searchRequest, 500, false)
</script>
<style scoped>
.searchbar {
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: var(--radius-sm);
    border: 1px solid var(--indigo-200);
    width: fit-content;
    height: 40px;
    padding-left: 8px;
    padding-right: 8px;
    background-color: var(--surface-primary);

    & .searchbar-input {
        border: none;
        width: 20px;
        transition: all 250ms ease;
        background-color: var(--surface-primary) !important;
    

        &.has-value {
            width: 100px;
        }

        &:focus-visible {
            width: 200px;
            border: none;
            outline: none;
        }
    }

    & .searchbar-icon {
        color: var(--indigo-300);
    }

    &:has(input:focus-visible) {
        border-color: var(--indigo-500);
    }

    &:has(input:focus-visible) .searchbar-icon {
        color: var(--indigo-500);
    }
}

.search-results {
    width: 80vw;
    max-width: 1000px;
    min-height: 60vh;
}
</style>