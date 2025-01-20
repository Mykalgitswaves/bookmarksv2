<template>
    <BackBtn class="mb-20"/>
    
    <section class="settings-section">
        <p class="text-xl mb-2 fancy">Bio</p>
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
                <h2 class="text-xl fancy mb-5 mt-5 mr-5">Public information</h2>
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
    import { ref, reactive } from 'vue';
    import { useRoute } from 'vue-router'
    import { db } from '../../services/db';
    import { urls } from '../../services/urls';
    import FormInputCluster from './settings/FormInputCluster.vue';
    
    const route = useRoute();
   
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