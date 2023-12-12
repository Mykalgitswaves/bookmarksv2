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
                    @click="router.push(pathToSettings + '?set_image=yes')"
                >
                    <IconEdit />
                </button>
            </div>
            <div class="u-p-h-text-info">
                <h2 class="font-medium text-slate-600 text-xl">
                    {{ userData?.username }}
                </h2>
                <p class="text-center fancy text-lg text-indigo-600">{{ userData?.bio }}</p>
            </div>
        </div>
        <div class="user-profile-subheader">
            <FriendButton 
                v-if="userData?.relationship_to_current_user !== 'self'"
                :current-option="userData?.relationship_to_current_user || 'loading'"
            />    
            
            <div class="user-profile-subheader-nav">
                <button
                    type="button"
                    :class="{ 'current-selection': currentSelection === 'about_me' }"
                    @click="currentSelection = 'about_me'"
                >
                    About me
                </button>

                <button
                    type="button"
                    :class="{ 'current-selection': currentSelection === 'bookshelves' }"
                    @click="currentSelection = 'bookshelves'"
                >
                    Bookshelves
                </button>
            </div>
        </div>   
        
        <component :is="componentMapping[currentSelection].component" :props="componentMapping[currentSelection].props"/>
    </section>
    <div class="mobile-menu-spacer sm:hidden"></div>
</template>
<script setup>
import BackBtn from './partials/back-btn.vue';
import { db } from '../../services/db';
import { urls } from '../../services/urls';
import { ref, reactive, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import path from '../svg/placeholderImg.png';

import IconEdit from '../svg/icon-edit.vue';
import IconLink from '../svg/icon-link.vue';
import IconPlus from '../svg/icon-plus.vue';
import AboutMe from './userpage/UserPageAboutMe.vue'
import LoadingIndicatorBook from '../feed/partials/LoadingIndicatorBook.vue';
import FriendButton from './userpage/UserFriendButton.vue';

const route = useRoute();
const router = useRouter();
const { user_profile } = route.params;
const pathToSettings = `/feed/${user_profile}/settings`

const userData = reactive({
        loaded: false,
        username: 'loading',
        full_name: '',
        password: '',
        email: '',
        bio: '',
        cdnUrl: ''
    });

const mutualPlaceholder = ['michael', 'kyle', 'cole']
const currentSelection = ref('about_me')

const componentMapping = reactive({
    'about_me': {
        component: AboutMe,
        props: {
            'user': user_profile
        }
    }
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
        userData.relationship_to_current_user = res.data.relationship_to_current_user
    });
};


function getUserBio() {
    return userData.relationship_to_current_user === 'self' ?
        (userData?.bio ?? 'Make sure to set your bio') :
        userData?.bio
}

onMounted(() => {
    getUserData(); 
    userData.bio = getUserBio()
})
         
</script>

<style scoped>

</style>