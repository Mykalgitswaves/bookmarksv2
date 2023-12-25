<template>
    <footer :class="isMinimized" class="lg:border-solid border-indigo-100 border-[1px]">
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
            @click="goToSearchPage(user)"
            aria-roledescription="navigation button"
        >
            <button 
                class="footer-nav-button" 
                type="button"
                @click="goToSearchPage(user)"
            >
                <IconSearch/>
            </button>
            <p>Search</p>
        </div>

        <div 
            class="nav-button-group hover:bg-gray-200" 
            @click="goToFeedPage(user)"
            aria-roledescription="navigation button"
        >
            <button 
                class="footer-nav-button" 
                type="button"
                alt="feed"
                @click="goToFeedPage(user)"
            >
                <IconBook/>
            </button>
            <p>Feed</p>
        </div>

        <div 
            class="nav-button-group hover:bg-gray-200"
            v-show="!isSearchBarActive"
            @click="goToSocialPage(user)"
            aria-roledescription="navigation button"
        >
            <button 
                class="footer-nav-button"
                type="button"
                @click="goToSocialPage(user)"
                alt="feed"
            >
                <IconSocial/>
            </button>
            <p>Social</p>
        </div>

        <div 
            class="nav-button-group hover:bg-gray-200"
            v-show="!isSearchBarActive"
            @click="goToUserPage(user)"
            aria-roledescription="navigation button"
        >
            <button 
                class="footer-nav-button"
                alt="feed"
                typ="button"
                @click="goToUserPage(user)"
            >
                <IconExplore/>
            </button>
            <p>Profile</p>
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
import { goToSearchPage, goToFeedPage, goToSocialPage, goToUserPage } from './footernavService';

const isSearchBarActive = ref(false);

const route = useRoute();
const { user } = route.params

window.addEventListener('toggleSearchBar', () => {
    isSearchBarActive.value = !isSearchBarActive.value
    console.log('fired event ', isSearchBarActive.value)
});

const minimized = ref(Boolean);
const isMinimized = computed(() => minimized.value === true ? 'minimized' : '');

function toggleMinimize() {
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
    background: linear-gradient(45deg, rgba(235, 241, 255, 1), rgba(255,255,255,0.8));
    backdrop-filter: blur(5px);
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
        background: linear-gradient(45deg, rgba(235, 241, 255, 0.5), rgba(255,255,255,0));
        backdrop-filter: blur(5px);
        margin-left: 1ch;
        border-radius: .75rem;
        margin-top: 10rem;
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
        justify-content: space-between;
        border-radius: .5rem;
        width: 100%;
        height: 40px;
    }

    .nav-button-group:first-of-type :hover {
        transform: scaleX(1.05);
        transition: all 150ms ease-in-out;
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
    padding: .25rem;
    margin-left: .5rem;
    margin-right: 1ch;
    color: #667EEA;
    align-content: center;
    justify-content: center;
    transition-duration: 250ms;
}
.footer-nav-button:hover {
    color: #343fa9;
    transform: scale(1.02);
}
</style>