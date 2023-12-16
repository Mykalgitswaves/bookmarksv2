<template>
    <BackBtn/>
    <section class="social-wrapper">
        <h1 class="text-2xl text-slate-800 font-medium">
            <span class="text-indigo-500 underline mr-2">{{ friend_requests.length }}</span> Pending requests
        </h1>

        <div class="friend-requests">
            
            <FriendRequest 
                v-for="(user, index) in current_requests" 
                :key="index"
                :num="index"
                :user="user"
            />
        </div>

        <SocialPagination :current-page="currentPage" :total-pages="totalPages" @page-changed="handlePageChange"/>
    </section>
</template>
<script setup>
    import BackBtn from '../partials/back-btn.vue';
    import FriendRequest from './FriendRequest.vue';
    import SocialPagination from './SocialPagination.vue';
    import { ref, computed } from 'vue';
    import { users } from '../../../fixtureData/dummyUsers.js';

    const friend_requests =  users;

    const currentPage = ref(0);
    const reqsPerPage = 4
    const totalPages = ref(Math.ceil(friend_requests.length / reqsPerPage));

    const current_requests = computed(() => { 
        const startingIndex = currentPage.value * reqsPerPage;
        const endingIndex = startingIndex + reqsPerPage;
        console.log(friend_requests.slice(startingIndex, endingIndex));

        return friend_requests.slice(startingIndex, endingIndex);
    });

    function handlePageChange(page) {
        currentPage.value = page;
    }
</script>
<style scoped lang="scss">
    .social-wrapper {
        margin-top: 24px;
        margin-left: 12px;
        margin-right: 12px;
        max-width: 880px;
    }

    .friend-requests {
        display: grid;
        grid-template-rows: repeat(auto-fit, 80px);
        grid-auto-flow: row;
        row-gap: 12px;
        margin-top: 20px;
        margin-bottom: 20px;
        height: 350px;
    }

    /* Maybe save maybe trash #TODO: Figure out this shit */
    /* .grid-row-readers {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
    }

    .reader {
        padding: 1rem;
        border-radius: 4px;
        display: flex;
        flex-direction: column;
        transition: background 200ms ease-in-out;
        align-items: start;
        background: var(--background-container-gradient);
    }

    .reader:hover {
        background: var(--hover-container-gradient);
        transition: all 200ms ease-in-out;
    }


    .reader button {
        width: 100%;
    } */
</style>