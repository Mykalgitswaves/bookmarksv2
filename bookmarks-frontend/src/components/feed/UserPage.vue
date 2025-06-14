<template>
    <section class="section-wrapper">
        <div class="user-profile-header">
            <div class="u-p-h-text-info">
                <h2 class="font-medium text-stone-600 text-xl fancy">
                    {{ userData?.username }}
                </h2>
                <p class="text-center fancy text-lg text-indigo-600">{{ userData?.bio }}</p>
            </div>
        </div>
        <div class="user-profile-subheader">
            <FriendButton 
                v-if="user !== user_profile"
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
                    class="bookshelves-btn flex items-center"
                    :class="{ 
                        'current-selection': currentSelection === 'reviews',
                    }"
                    @click="currentSelection = 'reviews'"
                >
                    My reviews
                </button>

                <button
                    type="button"
                    class="bookshelves-btn flex items-center"
                    :class="{ 
                        'current-selection': currentSelection === 'bookshelves',
                        'disabled': true
                    }"
                    disabled="true"
                    @click="currentSelection = 'bookshelves'"
                >   
                    Bookshelves
                    <IconLock class="ml-2" />
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
import svgPlaceholder from '../svg/placeholderImage.vue';

import IconEdit from '../svg/icon-edit.vue';
import IconLock from '../svg/icon-lock.vue';
import AboutMe from './userpage/UserPageAboutMe.vue'
import FriendButton from './userpage/UserFriendButton.vue';
import MyReviews from './userpage/MyReviews.vue';

const route = useRoute();
const router = useRouter();
const { user, user_profile } = route.params;
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

const currentSelection = ref('about_me')

const componentMapping = reactive({
    'about_me': {
        component: AboutMe,
        props: {
            'user': user_profile
        }
    },
    'reviews': {
        component: MyReviews,
    }
});

async function getUserData() {
    await db.get(urls.user.getUser(user_profile), null, true, (res) => {
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
        (userData?.bio !== '' ? userData?.bio : 'Make sure to set your bio') :
        userData?.bio
}

onMounted(async () => {
    await getUserData(); 
    userData.bio = getUserBio()
});
         
</script>

<style scoped>
    
    .bookshelves-btn.disabled {
        pointer-events: none;
        cursor: not-allowed;
    }
    
</style>