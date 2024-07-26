<template>
    <div class="update-previews">
        <PreviewCanvas
            v-if="loaded"
            :progress-bar-data="progressBarData"
            :preview-data="updatePreviewData" 
            :total-pages="totalPages"
            @modelValue:changed="(pagePayload) => debouncedSearchForUpdates(pagePayload)"
        />
        
        <PreviewSearchResults 
            :book-id="book.id"
            :post-previews="updatePreviewData.updates" 
            :is-loading-results="loading"    
        />
    </div>
</template>
<script setup>
import { computed, ref, onBeforeMount } from 'vue';
import { useRoute } from 'vue-router';
import { db } from '../../../services/db';
import { urls } from '../../../services/urls';
import { helpersCtrl} from '../../../services/helpers';
import PreviewCanvas from './PreviewCanvas.vue';
import PreviewSearchResults from './PreviewSearchResults.vue';

const props = defineProps({
    book: {
        type: Object,
        required: true,
    },
    currentPage: {
        type: Number,
    },
    totalPages: {
        type: Number,
    },
});

let rangeSize = Math.ceil(props.totalPages / 6);
const errorMessages = ref([]);
const startingPage = ref(0);

const updatePreviewData = ref({
    updates: [],
    remainingUpdates: null,
});


const updateCache = {};

const progressBarData = ref({
    defaultPageRange: rangeSize,
    weights: null,
});

const loaded = ref(false);
const route = useRoute();

const { debounce, throttle } = helpersCtrl;
const { user } = route.params;

async function searchForUpdates(page) {
    return await db.get(
        urls.rtc.getUpdatesForCurrentlyReadingPageRange(user, props.book.id),
        {
            starting_page_for_range: page,
            size_of_range: rangeSize,
        }, false,
    );
}

function updatesSuccessFunction(data) {
        updateCache[startingPage.value] = data.updates;

        updatePreviewData.value.updates = data.updates;
        updatePreviewData.value.remainingUpdates = data.additional_updates_not_shown ? data.additional_updates_not_shown : updatePreviewData.value.remainingUpdates;
}

onBeforeMount(async () => {
    // #TODO: Fix this so that it calls updates for books in a shelf so we can render previews for them inside update bookshelves.
    function progressSuccessFunction(data) {
        progressBarData.value.weights = data.weights;
        progressBarData.value.defaultPageRange = data.default_page_range;
    }

    
    const { user } = route.params;
    
    const progressBarRequest = await db.get(
        urls.rtc.getProgressBarForBookUpdates(user, props.book.id), 
        null, false,
    );

    const updatesRequest = await searchForUpdates(0);

    Promise.all([progressBarRequest, updatesRequest]).then(([progressResData, updatesResData]) => {
        progressSuccessFunction(progressResData)
        updatesSuccessFunction(updatesResData)
        loaded.value = true;
    }).catch((err) => {
        errorMessages.value = err;
    });
});

function _undebouncedDebounceFunctionToDebounce(page) {
    startingPage.value = page;

    const updates = updateCache[page];
    if (updates?.length) {
        updatesSuccessFunction({updates: updates});
        return
    }

    const rawUpdates = searchForUpdates(page)
    Promise.resolve(rawUpdates).then(data => {
        updatesSuccessFunction(data)
    });
}

const debouncedSearchForUpdates = debounce(_undebouncedDebounceFunctionToDebounce, 400, false);

</script>
<style scoped>
.progress-bar-container {
    display: flex;
    margin-top: 12px;
    margin-bottom: 4px;
    border-radius: 4px;
    overflow: clip
}

.progress-bar {
 height: 2px;
 background-color: var(--stone-200);
 display: inline-block;

 &.remainder {
    width: auto;
    background-color: var(--stone-100);
 }
}
</style>