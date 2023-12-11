<template>
    <BackBtn/>
    <section class="settings-section">
        <div class="edit-profile-picture">
            <img v-show="!isEditingProfileImage" :src="cdnUrl || path" alt="" :class="{'image-loading': loadingImageSave}">
            <button
                v-if="!isEditingProfileImage"
                type="button"
                class="edit-btn text-indigo-600 underline"
                @click="isEditingProfileImage = true"
            >
                    Change profile photo                
            </button>
            <div
                v-show="isEditingProfileImage"
                class="upload-care-component"
            >
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

            <button
                v-if="isEditingProfileImage"
                type="button"
                class="edit-btn"
                @click="isEditingProfileImage = false"
            >
                <IconExit/>
                cancel
            </button>
        </div>

        <p class="text-xl font-semibold mb-2">Bio</p>
        <div class="settings-info-bio">
            <textarea name="bio" id="" cols="30" rows="3" :disabled="isEditing" v-model="userData.bio"></textarea>
            <button 
                type="button"
                class="save-btn mt-5"
                @click="updateFieldName(userData.bio, 'bio')"
            >
                save
            </button>
        </div> 

        <div>
            <div class="flex items-center">
                <h2 class="text-xl font-semibold mb-5 mt-5 mr-5">Public information</h2>
            </div>

            <div class="settings-info-form" :class="{'loading': !userData.loaded}">
                <FormInputCluster 
                    input-id="user-name" 
                    name="username" 
                    type="text"   
                    :value="userData.username"
                    @new-value-saved="($event) => updateFieldName($event, 'user-name')"
                />

                <FormInputCluster 
                    input-id="email" 
                    name="email" 
                    type="email"    
                    :value="userData.email"
                    :is-save-disabled="!isEmailDisabled"
                    @updated:string="($event) => inputContainsEmail($event)"
                    @new-value-saved="($event) => updateFieldName($event, 'email')"
                />

                <FormInputCluster 
                    input-id="password" 
                    name="password" 
                    type="password"    
                    :value="userData.password"
                    @new-value-saved="($event) => updateFieldName($event, 'password')"
                />
            </div>
        </div>
    </section>
    <div class="mobile-menu-spacer sm:hidden"></div>
</template>

<script setup>
    import BackBtn from './partials/back-btn.vue';
    import IconExit from '../svg/icon-exit.vue';
    import path from '../svg/placeholderImg.png'
    import { ref, onMounted, reactive } from 'vue';
    import { useRoute } from 'vue-router'
    import { db } from '../../services/db';
    import { urls } from '../../services/urls';
    import * as LR from "@uploadcare/blocks";
    import FormInputCluster from './settings/FormInputCluster.vue';
    
    const route = useRoute();
    // To tell us when our stuff is saved dude.
    let cdnUrl = ref('');
    let loadingImageSave = false;
    const isEditingProfileImage = ref(false);
    //upload care stuff dont fuck with
    LR.registerBlocks(LR);

    // More uploadCare, Needs to be onMounted so query selector doesn't return null.
    onMounted(() => {
        const dataOutput = document.querySelector('lr-data-output');
        dataOutput.addEventListener('lr-data-output', (e) => {
            loadingImageSave = true;
            cdnUrl.value = e.detail.data.files[0].cdnUrl;
            // 
            console.log(cdnUrl, 'Make sre it worksiguess');

            db.post(urls.user.setUserImgCdnUrl(route.params.user), {'cdn_url': cdnUrl.value}).then(() => {
                loadingImageSave = false;
            });
        });
        isEditingProfileImage.value = !!route.query.set_image
    })

    const userData = reactive({
        loaded: false,
        username: '',
        full_name: '',
        password: '',
        email: '',
        bio: ''
    });

    // Call user endpoint for data
    async function getUserSettings() {
        await db.get(urls.user.getUser(route.params.user)).then((res) => {
            userData.username = res.data.username
            userData.full_name = res.data.full_name
            userData.email = res.data.email
            userData.bio = res.data.bio
            userData.loaded = true;
            cdnUrl.value = res.data.profile_img_url
        });
    }

    getUserSettings();

    const urlsMapping = {
        "username": urls.user.updateUsername,
        "email": urls.user.updateEmail,
        "bio": urls.user.updateBio
    }
    
    let isEmailDisabled = ref(false)
    // probs should be done on backend and emails should be verified somewhere else.
    // #TODO: ^ Make this better before we deploy.
    const inputContainsEmail = (input) => {
        if(input.length){
            const email_suffix = /@.*\.com$/
            isEmailDisabled.value = email_suffix.test(input);
        } else {
            isEmailDisabled.value = false
        }
    }

    // Changes to forms,functions
    function updateFieldName(newDataToSave, keyForMapping) {
        // Need this to say whether or not email save is disabled
        userData[keyForMapping] = newDataToSave;
        db.put(urlsMapping[keyForMapping](route.params.user), newDataToSave, true).then((res) => {
            userData[keyForMapping] = res.data;
        });
    }

    
</script>