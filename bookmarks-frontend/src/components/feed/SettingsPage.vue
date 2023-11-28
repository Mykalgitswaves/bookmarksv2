<template>
    <BackBtn/>
    <section class="settings-section">
        <div class="edit-profile-picture">
            <img :src="path" alt="">
            <button
                v-if="!isEditingProfileImage"
                type="button"
                class=" text-sm text-indigo-600 underline"
                @click="isEditingProfileImage = true"
            >
                    Change profile photo                
            </button>

            <button
                v-if="isEditingProfileImage"
                type="button"
                class="edit-btn profile-image"
                @click="isEditingProfileImage = false"
            >
                
                    <IconExit/>
                    cancel
            </button>

            <div>
                <input 
                    v-if="isEditingProfileImage"
                    type="file"
                />
            </div>
        </div>

        <div class="settings-info-form-container">
            <div>
                <div class="flex items-center">
                    <h2 class="text-xl font-semibold mb-5 mt-5 mr-5">Public information</h2>
                </div>

                <div class="settings-info-form" :class="{'loading': !userData.loaded}">
                    <label for="user-name">
                        <p class="text-sm text-slate-600 mb-2">username</p>
                        <input
                            type="text"
                            id="user-name"
                            class="settings-info-form-input"
                            v-model="userData.username"
                        >
                    </label>

                    <label for="email">
                        <p class="text-sm text-slate-600 mb-2">email</p>
                        <input type="email" id="user-email" class="w-100 py-1 px-2 rounded-md">
                    </label>

                    <label for="password">
                        <p class="text-sm text-slate-600 mb-2"
                        >password</p>
                        <input type="text" id="user-password" class="w-100 py-1 px-2 rounded-md">
                    </label>
                </div>
            </div>
            <div>
                <h2 class="text-xl font-semibold mb-5 mt-5">Associated accounts</h2>
                <div class="settings-info-form" :class="{'loading': !userData.loaded}">
                    <label for="user-social-instagram">
                        <p class="text-sm text-slate-600 mb-2">instagram</p>
                        <input type="text" id="user-social-instagram" class="settings-info-form-input">
                    </label>

                    <label for="user-social-twitter">
                        <p class="text-sm text-slate-600 mb-2">twitter</p>
                        <input type="text" id="user-social-twitter" class="w-100 py-1 rounded-md">
                    </label>

                    <label for="user-social-medium">
                        <p class="text-sm text-slate-600 mb-2">medium</p>
                        <input type="text" id="user-social-medium" class="w-100 py-1 rounded-md">
                    </label>
                </div>
            </div>
        </div>
    </section>
    <div class="mobile-menu-spacer sm:hidden"></div>
</template>
<script setup>
    import BackBtn from './partials/back-btn.vue';
    import IconEdit from '../svg/icon-edit.vue';
    import IconExit from '../svg/icon-exit.vue';
    import path from '../svg/placeholderImg.png'
    import { ref } from 'vue';
    import { useRoute } from 'vue-router'
    import { db } from '../../services/db';
    import { urls } from '../../services/urls';
    
    const isEditingProfileImage = ref(false);
    const isEditingProfileForm = ref(false);
    const userData = ref({
        loaded: false,
        username: '',
        full_name: '',
        password: '',
        email: ''
    });

    const route = useRoute();

    // Call user endpoint for data
    async function getUserSettings() {
        await db.get(urls.user.getUser(route.params.user)).then((res) => {
            userData.value = res.data
            userData.value.loaded = true;
        });
    }

    getUserSettings();
</script>