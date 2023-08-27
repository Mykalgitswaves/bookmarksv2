<template>
    <footer class="bg-white">
        <searchBar/>
        <div 
            :class="'nav-button-group hover:bg-gray-200' + isFeedActive" 
            v-show="!isSearchBarActive"
        >
            <button class="footer-nav-button" alt="feed">
                <IconBook/>
            </button>
            <p>Feed</p>
        </div>

        <div 
            :class="'nav-button-group hover:bg-gray-200' + isSocialActive"
            v-show="!isSearchBarActive"
        >
            <button class="footer-nav-button" alt="feed">
                <IconSocial/>
            </button>
            <p>Social</p>
        </div>

        <div 
            :class="'nav-button-group hover:bg-gray-200' + isExploreActive"
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
import searchBar from './navigation/searchBar.vue'


import { useRoute }  from 'vue-router'
import { computed, ref } from 'vue'


const isSearchBarActive = ref(false);

const route = useRoute()

const activeBorderClasses = 'border-solid border-2 border-indigo-300'

const isFeedActive = computed(() => {
    return route.path.includes('feed') ? activeBorderClasses : ''
})

const isSocialActive = computed(() => {
    return route.path.includes('social') ? activeBorderClasses : ''
})

const isExploreActive = computed(() => {
    return route.path.includes('explore') ? activeBorderClasses : ''
})

window.addEventListener('toggleSearchBar', () => {
    isSearchBarActive.value = !isSearchBarActive.value
    console.log('fired event ', isSearchBarActive.value)
})



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
    min-width: 10ch;
    display: flex;
    justify-content: space-around;
    padding: 1rem;
    background: rgba(243, 244, 246, 98%);
}

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
        flex-direction: column;
        flex-basis: 1;
        justify-content: space-around;
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