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

    <Overlay>
        <template #overlay-main>

        </template>
    </Overlay>
</template>
<script setup>
import { ref } from 'vue';
import { urls } from '../../../services/urls';
import { db } from '../../../services/db';
import { helpersCtrl } from '../../../services/helpers';
import { PubSub } from '../../../services/pubsub';
import IconSearch from '@/components/svg/icon-search.vue';
import Overlay from '../partials/overlay/Overlay.vue';

const { debounce } = helpersCtrl;
const search_params = ref('');
const responseBlob = ref({});

function searchRequest() {
    if (search_params.value.length > 1) {
        return db.get(urls.search(search_params.value), null, false, (res) => {
            responseBlob.value = res.data;
        }, (err) => {
            console.error(err)
        })
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
</style>