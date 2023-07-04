<template>
    <footer class="bg-white">
        <div class="nav-button-group hover:bg-gray-200"
            :class="isFeedActive ? 'border-solid border-2 border-indigo-300' : ''"
        >
            <button class="footer-nav-button" alt="feed">
                <IconBook/>
            </button>
            <p>Feed</p>
        </div>

        <div 
            class="nav-button-group hover:bg-gray-200"
            :class="isSocialActive ? 'border-solid border-2 border-indigo-300' : ''"
        >
            <button class="footer-nav-button" alt="feed">
                <IconSocial/>
            </button>
            <p>Social</p>
        </div>

        <div 
            class="nav-button-group hover:bg-gray-200"
            :class="isExploreActive ? 'border-solid border-2 border-indigo-300' : ''"
        >
            <button class="footer-nav-button" alt="feed">
                <IconExplore/>
            </button>
            <p>Explore</p>
        </div>
        <div 
            class="nav-button-group hover:bg-gray-200"
            :class="isSearchActive ? 'border-solid border-2 border-indigo-300' : ''"
        >
            <button class="footer-nav-button" alt="feed">
                <IconSearch/>
            </button>
            <p>Search</p>
        </div>
    </footer>
</template>


<script setup>
import IconBook from '@/components/svg/icon-book.vue'
import IconSocial from '@/components/svg/icon-social.vue';
import IconExplore from '@/components/svg/icon-explore.vue';
import IconSearch from '@/components/svg/icon-search.vue'
import { useRoute }  from 'vue-router'
import { computed } from 'vue'

const route = useRoute()

const isFeedActive = computed(() => {
    return route.path.includes('feed') ? true : false
})

const isSocialActive = computed(() => {
    return route.path.includes('social') ? true : false
})

const isExploreActive = computed(() => {
    return route.path.includes('explore') ? true : false
})

const isSearchActive = computed(() => {
    return route.path.includes('search') ? true : false
})
</script>

<style scoped>
footer {
    position: fixed;   
    bottom: 0;
    left: 0;
    width: 100%;
    display: flex;
    justify-content: space-around;
    padding: 1rem;
    background: rgba(243, 244, 246, 98%);
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