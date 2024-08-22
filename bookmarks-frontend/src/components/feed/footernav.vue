<template>
    <footer :class="{ 'minimized': minimizeFooter }"  
        class="lg:border-solid border-indigo-100 border-[1px]"
    >
        <!-- <div class="nav-button-group hover:bg-gray-200" 
            @click="goToSearchPage(user)"
            aria-roledescription="navigation button"
        >
            <button class="footer-nav-button" 
                type="button"
                @click="goToSearchPage(user)"
            >
                <IconSearch/>
            </button>

            <p>Search</p>
        </div> -->

        <div class="nav-button-group hover:bg-gray-200" 
            @click="goToFeedPage(user)"
            aria-roledescription="navigation button"
        >
            <button 
                class="footer-nav-button" 
                type="button"
                alt="feed"
                @click="goToFeedPage(user)"
            >
                <IconFeed/>
            </button>

            <p class="fancy text-stone-600">Feed</p>
        </div>
        
        <div class="nav-button-group hover:bg-gray-200"
            v-show="!isSearchBarActive"
            @click="goToBookshelvesPage(user)"
            aria-roledescription="navigation button"
        >
            <button 
                class="footer-nav-button"
                alt="feed"
                typ="button"
                @click="goToBookshelvesPage(user)"
            >
                <IconBookshelves/>
            </button>

            <p class="fancy text-stone-600">Bookshelves</p>
        </div>

        <div class="nav-button-group hover:bg-gray-200" 
            @click="goToFeedPage(user)"
            aria-roledescription="navigation button"
        >
            <button 
                class="footer-nav-button" 
                type="button"
                alt="feed"
                @click="goToFeedPage(user)"
            >
                <IconFeed/>
            </button>

            <p class="fancy text-stone-600">Notes</p>
        </div>

        <div class="nav-button-group hover:bg-gray-200"
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
                <IconProfile/>
            </button>

            <p class="fancy text-stone-600">Connections</p>
        </div>

        <div class="nav-button-group hover:bg-gray-200"
            v-show="!isSearchBarActive"
            @click="goToBookClubsPage(user)"
            aria-roledescription="navigation button"
        >
            <button 
                class="footer-nav-button"
                alt="feed"
                typ="button"
                @click="goToBookClubsPage(user)"
            >
            clubs
            </button>

            <p class="fancy text-stone-600">Book clubs</p>
        </div>
    </footer>

    <Transition name="content" tag="div">
        <div v-if="minimizeFooter"
            @click="minimizeFooter = false"
            @mouseover="minimizeFooter = false"
        >
            <div class="show-footer-nav">
                <span class="message">Show nav</span>
            </div>
        </div>
    </Transition>
</template>


<script setup>
import IconBook from '@/components/svg/icon-book.vue'
import IconSocial from '@/components/svg/icon-social.vue';
import IconFeed from '@/components/svg/icon-feed.vue';
// import searchBar from './navigation/searchBar.vue'
import IconSearch from '@/components/svg/icon-search.vue';
import IconProfile from '../svg/icon-profile-nav.vue';
import { useRoute }  from 'vue-router'
import IconBookshelves from '../svg/icon-bookshelves.vue'
import { ref } from 'vue'
import { goToSearchPage, 
    goToFeedPage,
    goToSocialPage,
    goToUserPage,
    goToBookshelvesPage,
    goToBookClubsPage
} from './footernavService';
import { debounce, throttle } from 'lodash';

const isSearchBarActive = ref(false);
const minimizeFooter = ref(false);

const route = useRoute();
const { user } = route.params

window.addEventListener('toggleSearchBar', () => {
    isSearchBarActive.value = !isSearchBarActive.value
});

if(window.visualViewport.width <= 768){
    window.addEventListener('scroll', function(event) {
        function footer() {
            var scroll = window.scrollY || document.documentElement.scrollTop;

            if (scroll < 50) {
                minimizeFooter.value = false;
            } else {
                minimizeFooter.value = true;
            }
        }

        footer();
    });
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

footer.minimized {
    display: none !important;
    position: absolute;
    bottom: -100px !important;
    left: 0;
    transition: 250ms;
}

footer .nav-button-group {
    padding: 0;
}

.show-footer-nav {
    position: fixed;
    padding: 14px 24px;
    width: 80px;
    background-color: var(--indigo-300);
    border-radius: var(--radius-sm);
    bottom: 10px;
    left: 50%;
    transform: translate(-50%, 0);
    opacity: 0.95;
    transition-duration: 250ms;
}

.show-footer-nav:hover {
    background-color: var(--indigo-200);
    cursor: pointer;
    width: 100px;
}

.show-footer-nav .message {
    position: absolute; 
    bottom: 30px;
    left: 50%;
    width: 80px;
    transform: translateX(-50%);
    text-align: center;
    white-space: nowrap;
    font-size: var(--font-lg);
    font-family: var(--fancy-script);
    color: var(--indigo-500);
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
    gap: .15rem;
    cursor: pointer;
    color: #5A67D8;
    font-weight: 500;
    padding: .4rem .25rem ;
    border-radius: .5rem;
}

.nav-button-group p {
    font-size: var(--font-xs);
}

@media only screen and (min-width: 768px) {
    footer {
        position: sticky;
        top: 15vh;
        width: min-content;
        max-width: 200px;
        height: calc(100% - 100px);
        display: flex;
        flex-direction: column;
        justify-content: start;
        gap: 2.5rem;
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
        display: grid;
        justify-content: center;
        border-radius: .5rem;
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
            font-size: var(--font-sm);
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

.desktop-footer {
    position: fixed;
    left: 0;
    top: 0;
    height: 100%;
}
</style>