<template>
    <BackBtn/>
    <section class="settings-section">
        <div class="edit-profile-picture">
            <img :src="cdnUrl || path" alt="" :class="{'image-loading': loadingImageSave}">
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

            <div class="upload-care-component">
                <lr-config
                    ctx-name="my-uploader"
                    pubkey="f4cae066507591578e32"
                    :maxLocalFileSizeBytes="10000000"
                    :multiple="false"
                    :imgOnly="true"
                ></lr-config>

                <lr-file-uploader-minimal
                    css-src="https://cdn.jsdelivr.net/npm/@uploadcare/blocks@0.25.0/web/lr-file-uploader-minimal.min.css"
                    ctx-name="my-uploader"
                    class="my-config"
                ></lr-file-uploader-minimal>
                
                <lr-data-output
                    ctx-name="my-uploader"
                    use-console
                    use-input
                    use-group
                    use-event
                ></lr-data-output>
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
    import IconExit from '../svg/icon-exit.vue';
    import path from '../svg/placeholderImg.png'
    import { ref, onMounted } from 'vue';
    import { useRoute } from 'vue-router'
    import { db } from '../../services/db';
    import { urls } from '../../services/urls';
    import * as LR from "@uploadcare/blocks";

    // To tell us when our stuff is saved dude.
    let cdnUrl;
    let loadingImageSave = false;

    //upload care stuff dont fuck with
    LR.registerBlocks(LR);

    // More uploadCare, Needs to be onMounted so query selector doesn't return null.
    onMounted(() => {
        const dataOutput = document.querySelector('lr-data-output');
        dataOutput.addEventListener('lr-data-output', (e) => {
            loadingImageSave = true;
            cdnUrl = e.detail.data.files[0].cdnUrl;
            // 
            console.log(cdnUrl, 'Make sre it worksiguess');

            db.post(urls.user.setUserImgCdnUrl(route.params.user), cdnUrl).then(() => {
                loadingImageSave = false;
            });
        });
    })

    const isEditingProfileImage = ref(false);
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

    cdnUrl = userData.value.profile_img_url
</script>