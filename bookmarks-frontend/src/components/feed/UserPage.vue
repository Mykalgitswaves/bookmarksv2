<template>
    <BackBtn/>
    <section class="user-profile">
        <div class="user-profile-header">
            <div class="edit-profile-picture">
                <img :src="path" class="" alt="">
            </div>
            <h2 class="font-semibold text-slate-600 text-2xl">
                {{ userData?.username || 'loading' }}
            </h2>
        </div>
        <div class="user-profile-subheader">
            <p></p>
            <div>
                <button 
                    class="btn bg-indigo-500 text-white hover:bg-indigo-700"
                    type="button"
                >
                    add friend
                </button>
                <button 
                    class="btn bg-indigo-500 text-white hover:bg-indigo-700"
                    type="button"
                >
                    add friend
                </button>
            </div>
        </div>
    </section>    
</template>
<script setup>
import BackBtn from './partials/back-btn.vue';
import { db } from '../../services/db';
import { urls } from '../../services/urls';
import { useRoute } from 'vue-router';
import { ref } from 'vue';
import path from '../svg/placeholderImg.png'

const route = useRoute();
const { user } = route.params;
const userData = ref(null);

async function getUserData() {
    await db.get(urls.user.getUser(user), null, true).then((res) => {
        userData.value = res.data;
    });
};

getUserData();

</script>

<style scoped>
.user-profile-header {
    display: flex;
    justify-content: center;
    flex-direction: column;
    align-items: center;
}
</style>