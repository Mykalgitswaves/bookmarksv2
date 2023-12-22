<template>
    <BackBtn/>
    <section class="social-wrapper">
        <div class="accordian-heading">
            <h1 class="text-2xl text-slate-800 font-medium">
                <span class="text-indigo-500 underline mr-2">{{ totalRequests }}</span> Pending requests
            </h1>

            <button 
                type="button"
                alt="expand-collapse"
                class="accordian-heading-btn large"
                @click=""
            >
                <IconChevron />
            </button>
        </div>

        <div class="friend-requests">
            <FriendRequest 
                v-for="(user, index) in friend_requests" 
                :key="index"
                :num="index"
                :userData="user"
            />
        </div>

        <SocialPagination :current-page="currentPage" :total-pages="totalPages" @page-changed="handlePageChange"/>
    </section>
</template>
<script setup>
    import BackBtn from '../partials/back-btn.vue';
    import FriendRequest from './FriendRequest.vue';
    import SocialPagination from './SocialPagination.vue';
    import { ref, computed, onMounted } from 'vue';
    // import { users } from '../../../fixtureData/dummyUsers.js';
    import { useRoute } from 'vue-router'
    import { db } from '../../../services/db';
    import { urls } from '../../../services/urls';
    import IconChevron from '../../svg/icon-chevron.vue';
    const route = useRoute();

    const friend_requests =  ref(null);
    const currentPage = ref(1);
    const reqsPerPage = 4;
    const totalPages = ref(0);
    const totalRequests = ref(0);
    const current_requests = ref([]);

    onMounted(() => {
        db.get(urls.user.getUsersFriendRequests(route.params.user)).then((res) => {
            friend_requests.value = res.data
            totalRequests.value = friend_requests.value.length;
        });

        totalPages.value = computed(() => {
            if (friend_requests.value?.length) {
                Math.ceil(friend_requests.value.length / reqsPerPage);
            }
        });
    
        current_requests.value = computed(() => { 
            const startingIndex = 0;
            const endingIndex = reqsPerPage * currentPage.value;
            if (!startingIndex && !endingIndex) {
                return;
            }
            return friend_requests.value.slice(startingIndex, endingIndex);
        })
    });


    function handlePageChange(page) {
        currentPage.value = page;
    };
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
        min-height: 350px;
    }


    .accordian-heading {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
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