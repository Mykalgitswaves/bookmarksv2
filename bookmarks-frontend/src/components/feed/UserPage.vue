<template>
    <BackBtn/>
    
    <section class="section-wrapper">
        <div class="user-profile-header">
            <div class="edit-profile-picture">
                <img :src="userData?.cdnUrl || path" class="" alt="">
                <button
                    v-if="route.params.user === route.params.user_profile"
                    type="button"
                    class="e-p-p-btn"
                    @click="router.push(pathToSettings)"
                >
                    <IconEdit />
                </button>
            </div>
            <h2 v-if="userData.loaded" class="font-medium text-slate-600 text-xl mt-4">
                {{ userData?.username }}
            </h2>
        </div>
        <div class="user-profile-subheader">
                <LoadingIndicatorBook v-if="!userData.loaded"/>
                <button 
                    v-if="userData.loaded"
                    class="btn add-friend-btn"
                    type="button"
                >
                <IconPlus class="mr-2"/>
                add friend
                </button>

                <button        
                v-if="userData.loaded"
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
import { ref, reactive } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import path from '../svg/placeholderImg.png';

import IconEdit from '../svg/icon-edit.vue';
import IconLink from '../svg/icon-link.vue';
import IconPlus from '../svg/icon-plus.vue';
import AboutMe from './userpage/UserPageAboutMe.vue'
import LoadingIndicatorBook from '../feed/partials/LoadingIndicatorBook.vue';

const route = useRoute();
const router = useRouter();
const { user_profile } = route.params;
const userData = reactive({
        loaded: false,
        username: '',
        full_name: '',
        password: '',
        email: '',
        bio: '',
        cdnUrl: ''
    });

async function getUserData() {
    await db.get(urls.user.getUser(user_profile), null, true).then((res) => {
        userData.loaded = true
        userData.username = res.data.username
        userData.full_name = res.data.full_name
        userData.email = res.data.email
        userData.bio = res.data.bio
        userData.loaded = true;
        userData.cdnUrl = res.data.profile_img_url
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