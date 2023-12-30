<template>
    <BackBtn/>
    <section class="social-wrapper">
        <Accordian 
            :expanded="social_dropdowns['is-pending-requests-expanded']"
            @clicked-chevron="
                ($event) => 
                accordianFn('is-pending-requests-expanded', social_dropdowns, $event)
                "
        >
            <template v-slot:heading-text>
                <span class="text-indigo-500 underline mr-2">
                    {{ totalRequests || 'Loading' }}
                </span> Pending requests
            </template>
        </Accordian>

        <div 
            class="friend-requests"
        >
            <div v-if="friend_requests?.length && social_dropdowns['is-pending-requests-expanded']">
                <FriendRequest
                v-for="(user, index) in friend_requests" 
                :key="index"
                :num="index"
                :userData="user"
                />
                
                <SocialPagination v-if="totalPages > currentPage" :current-page="currentPage" :total-pages="totalPages" @page-changed="handlePageChange"/>
            </div>
        </div>
    </section>
    <section class="social-wrapper">
        <Accordian 
            :expanded="social_dropdowns['is-activities-expanded']"
            @clicked-chevron="
                ($event) => 
                accordianFn('is-activities-expanded', social_dropdowns, $event)
                "
        >
            <template v-slot:heading-text>
                Recent activity
            </template>
        </Accordian>
        <div class="activities" v-if="activities?.length && social_dropdowns['is-activities-expanded']">
                <Activity
                    v-for="activity in activities"
                    :key="activity.id"
                    :activity="activity"
                />
        </div>
    </section>
</template>
<script setup>
    import { ref, computed, onMounted, watchEffect, reactive } from 'vue';
    import { useRoute } from 'vue-router'
    import { db } from '../../../services/db';
    import { urls } from '../../../services/urls';

    import BackBtn from '../partials/back-btn.vue';
    import FriendRequest from './FriendRequest.vue';
    import SocialPagination from './SocialPagination.vue';
    import Accordian from '../partials/accordian.vue';
    import { accordianFn } from '../partials/accordianService';
    import Activity from './Activities/Activity.vue';
    

    const route = useRoute();
    // Used for all dropdown toggles.
    const social_dropdowns = reactive({});

    const friend_requests =  ref(null);
    const currentPage = ref(1);
    const reqsPerPage = 4;
    const totalPages = ref(0);
    const totalRequests = ref(0);
    const current_requests = ref([]);

    const activities = ref(null);

    onMounted(() => {
        db.get(urls.user.getUsersFriendRequests(route.params.user)).then((res) => {
            friend_requests.value = res.data
            totalRequests.value = friend_requests.value.length;
        });

        db.get(urls.user.getActivitiesForUser(route.params.user)).then((res) => {
            // Change this logic in the future so that social dropdowns depends on what is returned from request calls. 
            social_dropdowns['is-activites-expanded'] = !!res.data.length;
            activities.value = res.data;
        })

        totalPages.value = computed(() => {
            if (friend_requests.value?.length) {
                return Math.ceil(friend_requests.value.length / reqsPerPage);
            }
            return 0;
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

    watchEffect(() => {
        // Used to set a default value for dropdowns?
        social_dropdowns['is-pending-requests-expanded'] = () => 
            (totalRequests.value > 0 ? true : false)
        social_dropdowns['is-activities-expanded'] = () => 
            (activities.value ? true : false)
    });

</script>
<style scoped>
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
        min-height: fit-content;
        max-height:  350px;
    }


    .activities {
        display: grid;
        grid-template-columns: 1fr;
        row-gap: 20px;
        margin-top: 20px;
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