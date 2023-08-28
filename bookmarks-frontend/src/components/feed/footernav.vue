<template>
    <footer :class="'bg-slate-200 ' + isMinimized">
        <div class="nav-button-group hidden-on-mobile">
            <button 
                class="footer-nav-button"
                type="button"
                @click="toggleMinimize()"
            >
                <IconExpand/>
            </button>
        </div>

        <div
            class="nav-button-group hover:bg-gray-200" 
            @click="goToSearchPage()"
        >
            <button 
                class="footer-nav-button" 
                type="button"
                @click="goToSearchPage()"
            >
                <IconSearch/>
            </button>
            <p>Search</p>
        </div>

        <div 
            class="nav-button-group hover:bg-gray-200" 
            @click="goToFeedPage()"
        >
            <button 
                class="footer-nav-button" 
                type="button"
                alt="feed"
                @click="goToFeedPage()"
            >
                <IconBook/>
            </button>
            <p>Feed</p>
        </div>

        <div 
            class="nav-button-group hover:bg-gray-200"
            v-show="!isSearchBarActive"
        >
            <button class="footer-nav-button" alt="feed">
                <IconSocial/>
            </button>
            <p>Social</p>
        </div>

        <div 
            class="nav-button-group hover:bg-gray-200"
            v-show="!isSearchBarActive"    
        >
            <button class="footer-nav-button" alt="feed">
                <IconExplore/>
            </button>
            <p>Explore</p>
        </div>
    </footer>
</template>


<script setup>
import IconBook from '@/components/svg/icon-book.vue'
import IconSocial from '@/components/svg/icon-social.vue';
import IconExplore from '@/components/svg/icon-explore.vue';
// import searchBar from './navigation/searchBar.vue'
import IconSearch from '@/components/svg/icon-search.vue';
import IconExpand from '@/components/svg/icon-expand.vue';

import { useRoute, useRouter }  from 'vue-router'
import { computed, ref } from 'vue'

const isSearchBarActive = ref(false);

const route = useRoute();
const router = useRouter();

function goToSearchPage() {
    router.push(`/feed/${route.params.user}/search/`);
}

function goToFeedPage(){
    router.push(`/feed/${route.params.user}/review/all`);
}

const activeBorderClasses = 'border-solid border-2 border-indigo-300';

window.addEventListener('toggleSearchBar', () => {
    isSearchBarActive.value = !isSearchBarActive.value
    console.log('fired event ', isSearchBarActive.value)
})

const minimized = ref(Boolean);
const isMinimized = computed(() => minimized.value === true ? 'minimized' : '');

function toggleMinimize() {
    console.log('called')
    return minimized.value = !minimized.value
}
</script>

<style scoped>
.hidden {
    display: none !important;
}

footer {
    position: fixed;   
    bottom: 0;
    left: 0;
    width: 100%;
    min-width: min-content;
    display: flex;
    justify-content: space-around;
    padding: 1rem;
    background: rgba(243, 244, 246, 98%);
    transition-duration: 250ms;
    transition-timing-function: ease-in-out;
}


footer .nav-button-group {
    padding: 0;
}


footer.minimized .nav-button-group p { display: none;}

.searchbar {
    display: flex;
    flex-direction: column;
    flex-basis: 1;
    justify-content: space-around;
    color: #5A67D8;
    font-weight: 500;
}

.nav-button-group {
    display: grid;
    grid-template-columns: 1;
    justify-items: center;
    align-items: center;
    gap: .15rem;
    cursor: pointer;
    color: #5A67D8;
    font-weight: 500;
    padding: .4rem .25rem ;
    border-radius: .5rem;
}

.nav-button-group p {
    display: none;
}

@media only screen and (max-width: 1000px) {
    .nav-button-group p {
        display: none;
        visibility: hidden;
    }


    .hidden-on-mobile { 
        display: none !important;
        visibility: hidden;
    }
}

@media only screen and (min-width: 768px) {
    footer {
        position: sticky;
        top: calc(30vh);
        width: min-content;
        max-width: 200px;
        height: calc(100% - 274px);
        display: flex;
        flex-direction: column;
        justify-content: start;
        gap: 1.5rem;
        align-items: center;
        background: transparent
    }

    footer.minimized {
        max-width: 3ch;
        transition-duration: 250ms;
        transition-timing-function: ease-in-out;
    }

    .hidden-on-mobile { 
        display: block !important;
    }

    .nav-button-group {
        position: sticky;
        top: 3rem;
        display: flex;
        align-self: start;
        border-radius: .5rem;
    }

    /* #Todo: Make the search bar responsive so it looks better on mobile and desktop */
    .searchbar {
        display: flex;
        flex-direction: column;
        flex-basis: 1;
        justify-content: space-around;
    }
}


@media only screen and (min-width: 1130px) {
    .nav-button-group p {
            display: block;
            visibility: visible;
            padding: 0 1ch;
    }    
}


.footer-nav-button {
    border-radius: 50%;
    padding: .5rem;
    margin-left: .5rem;
    margin-right: .5rem;
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