<template>
    <BackBtn/>
    
    <section class="section-wrapper">
        <div class="user-profile-header">
            <div class="edit-profile-picture">
                <img :src="path" class="" alt="">
                <button
                    v-if="route.params.user === route.params.user_profile"
                    type="button"
                    class="e-p-p-btn"
                    @click="router.push(pathToSettings)"
                >
                    <IconEdit />
                </button>
            </div>
            <h2 class="font-medium text-slate-600 text-xl mt-4">
                {{ userData?.username || 'loading' }}
            </h2>
        </div>
        <div class="user-profile-subheader">
            <p></p>
            
                <button 
                    class="btn add-friend-btn"
                    type="button"
                >
                <IconPlus class="mr-2"/>
                add friend
                </button>

                <button        
                    class="mutuals-btn mt-2"
                    type="button"
                >
                    <IconLink class="mt-2"/>
                    {{ mutualPlaceholder[0] }}&nbsp;
                    <span v-if="mutualPlaceholder.length > 1">
                        and {{ mutualPlaceholder.length }} others
                    </span>
                </button>

                <div class="user-profile-subheader-nav">
                    <button
                        type="button"
                        @click="currentSelection = 'about_me'"
                    >
                        About me
                    </button>
                    <button>
                        Bookshelves
                    </button>
                </div>
        </div>
        <component :is="componentMapping[currentSelection]"/>
    </section>
    <div class="mobile-menu-spacer sm:hidden"></div>
</template>
<script setup>
import BackBtn from './partials/back-btn.vue';
import { db } from '../../services/db';
import { urls } from '../../services/urls';
import { useRoute, useRouter } from 'vue-router';
import { ref } from 'vue';
import path from '../svg/placeholderImg.png';

import IconEdit from '../svg/icon-edit.vue';
import IconLink from '../svg/icon-link.vue';
import IconPlus from '../svg/icon-plus.vue';
import AboutMe from './userpage/UserPageAboutMe.vue'

const route = useRoute();
const router = useRouter();
const { user_profile } = route.params;
console.log(user_profile)
const userData = ref(null);

async function getUserData() {
    await db.get(urls.user.getUser(user_profile), null, true).then((res) => {
        userData.value = res.data;
    });
};

getUserData();

const mutualPlaceholder = ['michael', 'kyle', 'cole']
const currentSelection = ref('about_me')

const componentMapping = {
    'about_me': AboutMe,
}; 

        
const pathToSettings = `/feed/${user_profile}/settings`

         
</script>

<style scoped>

</style>